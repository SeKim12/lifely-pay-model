from decimal import Decimal

from utils import processlogger
from utils.safe_decimals import geq, leq

from contracts import pool_factory, token_contract, balance_tracker, inflation_tracker
from contracts.types import Tokens

# from states import errors
from states.errors import PoolNotEnoughBalanceError
from states.params import Params
from states.events import Events
from states.interfaces import RouterI, AgentI, TokenI

from agents.oracle import Oracle

logger = processlogger.ProcessLogger()


class Router(RouterI):
    def __init__(self, va_denom: str, sa_denom: str):
        self._va_denom = va_denom  # 'ETH'
        self._sa_denom = sa_denom  # 'USDC'

        # Initiate Pools
        self._va_pool = pool_factory.VolatilePool(self._va_denom)
        self._sa_pool = pool_factory.StablePool(self._sa_denom)
        self._fee_pool = pool_factory.FeePool(self._sa_denom)

        # Initiate Token Contracts
        self._lp_tc = token_contract.LPTokenContract()
        self._erc_tc = token_contract.ERC1155TokenContract()

        # Initiate Trackers
        self._bt = balance_tracker.BalanceTracker(
            self._va_pool, self._sa_pool, self._fee_pool
        )
        self._it = inflation_tracker.InflationTracker(self._erc_tc, self._bt)

    @property
    def num_triggered(self):
        return self._bt.num_triggered

    @property
    def num_rebalanced(self):
        return self._bt.num_rebalanced

    @property
    def is_accepting_liquidity(self):
        """
        Liquidity Providing is capped at 2M, and Initial Liquidity is 1M.
        """
        return self._sa_pool.principal <= (Params.stake_cap() * 2)

    @property
    def va_denom(self):
        return self._va_denom

    @property
    def sa_denom(self):
        return self._sa_denom

    def process_buyer_buy_request(self, buyer: AgentI, tokens_va: TokenI):
        """
        Buyer Scenario - BUY

        Steps:
            1. (external) buyer sends VA to contract with value equivalent to USD value of product
            2. VA tokens are deposited to pool
            3. Withdraw from USDC pool at different levels. Spillover to DANGER level is converted automatically
            4. Extract transaction fee and deposit to Fee Pool
            5. Mint voucher tokens to buyer, where amount is adjusted for the levels at which USDC was withdrawn
        """
        cur_price = Oracle.get_price_of(self._va_denom)
        logger.info(Events.Buyer.AttemptingBuy.fmt(buyer, tokens_va))
        self._va_pool.deposit(tokens_va)

        cost_sa = Oracle.exchange(tokens_va, self._sa_denom)

        auto_convert = cost_sa
        voucher_tokens = None

        # cannot withdraw anything from SA Pool if balance state is WARNING
        if not self._bt.warning:
            withdraw_steps_sa, auto_convert = self._bt.get_withdraw_amount_per_range(
                cost_sa
            )
            withdraw_steps_va = [
                Oracle.exchange(t, self._va_denom) for t in withdraw_steps_sa
            ]

            for tokens_sa in withdraw_steps_sa:
                if geq(tokens_sa.amount, 0):
                    self._handle(self._sa_pool.withdraw, tokens_sa)

            vc_amount = self._erc_tc.balance_adjusted_voucher_quantity(
                withdraw_steps_va
            )
            vc_denom = self._erc_tc.serialize_vouchers(cur_price)
            voucher_tokens = Tokens(vc_amount, vc_denom)

        # auto convert remaining amount
        # this would be the entire cost if warning state, or pool lacks balance
        if geq(auto_convert.amount, 0):
            self._automated_conversion(Oracle.exchange(auto_convert, self._va_denom))

        if voucher_tokens:
            self._erc_tc.mint_to(buyer, voucher_tokens)

        fee_sa = cost_sa.times(Params.tx_fee_rate())
        # self._sa_pool.deposit(fee_sa, protocol_injected=True)
        self._fee_pool.deposit(fee_sa)
        logger.info(Events.Buyer.SuccessBuy.fmt(buyer, tokens_va, cost_sa.amount))

        self._bt.rebalance()

    def process_buyer_redeem_request(self, buyer: AgentI, vc_tokens: TokenI):
        """
        Buyer Scenario - REDEEM

        Steps:
            1. (external) buyer sends voucher tokens to contract
            2. Calculate amount of VA that should be redeemed to buyer
            3. If there is nothing to redeem (DEFLATION or LOW BALANCE), return
            4. Burn voucher tokens (* this should be done AFTER Step 2 *)
            5. Redeem calculated amount of VA to buyer
            6. Extract Redemption Fee (Option Premium) and deposit to Fee Pool
        """
        logger.info(Events.Buyer.AttemptingRedeem.fmt(buyer, vc_tokens))

        redeem_usd = self._calculate_amount_to_redeem_buyer_usd(vc_tokens)
        # nothing to redeem, re-mint voucher tokens to buyer
        if leq(redeem_usd, 0):
            self._erc_tc.mint_to(buyer, vc_tokens)
            return self._bt.rebalance()

        self._erc_tc.burn(vc_tokens)
        redeem_va = Oracle.exchange(Tokens(redeem_usd, self._sa_denom), self._va_denom)
        redeem_va_minus_fees = redeem_va.times(1 - Params.op_premium())

        # redeem to buyer after extracting redemption fees
        self._va_pool.redeem_to(buyer, redeem_va_minus_fees)

        fee_va = redeem_va.times(Params.op_premium())
        # withdraw from VA pool and deposit to Fee pool
        self._va_pool.withdraw(fee_va)
        fee_sa = Oracle.exchange(fee_va, self._sa_denom)
        # self._sa_pool.deposit(fee_sa, protocol_injected=True)
        self._fee_pool.deposit(fee_sa)

        logger.info(
            Events.Buyer.SuccessRedeem.fmt(
                buyer, redeem_va_minus_fees, redeem_usd * (1 - Params.op_premium())
            )
        )

        self._bt.rebalance()

    def process_lp_provider_request(self, provider: AgentI, tokens_sa: TokenI):
        """
        LP Provider Scenario - PROVIDE

        Steps:
            1. (external) provider sends SA to contract
            2. Deposit SA to pool and mint LP tokens to provider
        """
        logger.info(Events.Provider.AttemptingProvide.fmt(provider, tokens_sa))

        # mint LP tokens pro rata. Initial liquidity is reference point, with that amount as 1 LP
        # Initial liquidity MUST be provided by protocol
        self._sa_pool.deposit(tokens_sa, protocol_injected=provider.type == "Protocol")
        amount_lp = self._sa_pool.calculate_lp_token_amount(tokens_sa)
        tokens_lp = Tokens(amount_lp, "LP")
        self._lp_tc.mint_to(provider, tokens_lp)

        logger.info(Events.Provider.SuccessProvide.fmt(provider, tokens_sa))

        # self._bt.rebalance()

    def process_lp_provider_redeem_request(self, provider: AgentI, tokens_lp: TokenI):
        """
        LP Provider Scenario - REDEEM

        Steps:
            1. (external) provider sends LP tokens to contract
            2. Calculate amount of SA (SA Pool + Fee) that should be redeemed to buyer
            3. Burn LP tokens (* this should be done AFTER Step 2 *)
            4. Redeem from SA Pool and Fee Pool to provider
        """
        logger.info(Events.Provider.AttemptingRedeem.fmt(provider, tokens_lp))

        lp_portion = self._lp_tc.calculate_lp_portion(tokens_lp)
        self._lp_tc.burn(tokens_lp)

        # NOTE: assuming that initial liquidity is provided by the protocol
        # Otherwise, we will double count principal and initial liquidity
        redeem_principal_amount = (
            self._sa_pool.principal + self._sa_pool.initial_liquidity
        ) * lp_portion
        redeem_sa = Tokens(redeem_principal_amount, self._sa_denom)

        redeem_fee_usd = self._fee_pool.balance * lp_portion
        redeem_fee = Tokens(redeem_fee_usd, self._sa_denom)

        # Liquidate VA Pool if necessary, and redeem to provider
        self._handle(self._sa_pool.redeem_to, provider, redeem_sa)
        # Redeeming from fee pool should not trigger any liquidation
        self._fee_pool.redeem_to(provider, redeem_fee)

        logger.info(
            Events.Provider.SuccessRedeem.fmt(provider, redeem_sa.plus(redeem_fee))
        )

        self._bt.rebalance()

    def dry_run_redeem_lp(self, tokens_lp: TokenI):
        """
        TODO: Not completely accurate; does not take into account balance of VA Pool
        """
        lp_portion = self._lp_tc.calculate_lp_portion(tokens_lp)
        redeem_principal_amount = (
            self._sa_pool.principal + self._sa_pool.initial_liquidity
        ) * lp_portion
        redeem_fee_usd = self._fee_pool.balance * lp_portion
        return redeem_principal_amount + redeem_fee_usd

    def _handle(self, func, *args):
        """
        Handler for withdrawals from SA Pool.
        If there are not enough funds initially, this will attempt to liquidate VA Pool, then retry once.
        """
        result, e = func(*args)
        if isinstance(e, PoolNotEnoughBalanceError):
            deficit = result
            liq_amount = Oracle.exchange(deficit, self._va_denom)
            self._va_pool.liquidate(liq_amount)
            self._sa_pool.deposit(deficit)
            result, e = func(*args)
            if e:
                raise e
        elif e:  # catch other errors
            raise e
        return
        # result, e = func(*args)
        # if isinstance(e, PoolNotEnoughBalanceError):
        #     deficit = result
        # extract_from_fee_pool = Tokens(
        #     min(deficit.amount, self._fee_pool.balance), "USDC"
        # )
        # self._fee_pool.withdraw(extract_from_fee_pool)
        # self._sa_pool.deposit(extract_from_fee_pool, protocol_injected=True)
        #
        # if geq(deficit.amount - extract_from_fee_pool.amount, 0):
        #     liq_amount = Oracle.exchange(deficit, self._va_denom)
        #     self._va_pool.liquidate(liq_amount)
        #     self._sa_pool.deposit(deficit, protocol_injected=True)
        #     result, e = func(*args)
        #     if e:
        #         raise e
        # elif e:  # catch other errors
        #     raise e
        # return result

    def _calculate_amount_to_redeem_buyer_usd(self, vc_tokens: TokenI) -> Decimal:
        # calculate the maximum rate of inflationary returns that can be redeemed to buyers
        r_m = self._it.calculate_max_redeem_rate()

        vc_amount, vc_denom = vc_tokens.decompose()
        og_price = self._erc_tc.deserialize_vouchers(vc_denom)

        # get inflation rate for the received voucher tokens
        inflation_rate = self._it.calculate_inflation(og_price)
        # if no inflation, or nothing to redeem (r_m == 0), return 0
        redeem_usd = og_price * vc_amount * inflation_rate * r_m

        if leq(redeem_usd, 0):
            cause = (
                "DEFLATION"
                if leq(inflation_rate, 0)
                else "LOW BALANCE"
                if leq(r_m, 0)
                else ""
            )
            logger.warning(Events.Router.NothingToRedeem.fmt(vc_tokens, cause))

        return redeem_usd

    def _automated_conversion(self, tokens: TokenI):
        logger.info(Events.Router.AttemptingAutomatedConversion.fmt(tokens))
        self._va_pool.liquidate(tokens)
