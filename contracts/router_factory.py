from typing import List, Tuple
from utils import processlogger, types, services
from contracts import pool_factory, token_contract, oracle, balance_observer
from contracts.inflation_tracker import InflationTracker
from states import events, errors
from states.params import Params
from states.events import Events

logger = processlogger.ProcessLogger()


class Router:

    def __init__(self):
        # Initiate Oracle
        self._oracle = oracle.Oracle()

        self._va_denom = 'ETH'
        self._sa_denom = 'USDC'

        # Initiate Pools
        self._va_pool = pool_factory.VolatilePool(self._va_denom)
        self._sa_pool = pool_factory.StablePool(self._sa_denom)
        self._fee_pool = pool_factory.FeePool(self._sa_denom)

        # Initiate and Register Balance Observer
        self._bobs = balance_observer.BalanceObserver(self._va_pool, self._sa_pool, self._fee_pool)
        self._va_pool.add_observer(self._bobs)
        self._sa_pool.add_observer(self._bobs)
        self._fee_pool.add_observer(self._bobs)

        # Initiate Token Contracts
        self._lp_tc = token_contract.LPTokenContract()
        self._erc_tc = token_contract.ERC1155TokenContract()

    def process_buyer_buy_request(self, buyer: types.AgentType, tokens_va: types.Tokens):
        """
        Buyer Scenario - BUY

        Steps:
            1. (external) buyer sends VA to contract with value equivalent to USD value of product
            2. VA tokens are deposited to pool
            3. Withdraw from USDC pool at different levels. Spillover to DANGER level is converted automatically
            4. Extract transaction fee and deposit to Fee Pool
            5. Mint voucher tokens to buyer, where amount is adjusted for the levels at which USDC was withdrawn
        """
        logger.info(Events.Buyer.AttemptingBuy.fmt(buyer, tokens_va))
        self._va_pool.deposit(tokens_va)
        withdraw_sa = self._oracle.exchange(tokens_va, self._sa_denom)
        withdraw_steps_sa, remaining_sa = self._calculate_withdraw_steps(withdraw_sa)
        withdraw_steps_va = [self._oracle.exchange(tokens_sa, self._va_denom) for tokens_sa in withdraw_steps_sa]

        for tokens_sa in withdraw_steps_sa:
            self._handle(self._sa_pool.withdraw, tokens_sa)

        remaining_va = self._oracle.exchange(remaining_sa, self._va_denom)
        if remaining_va.amount > 0:
            self._automated_conversion(remaining_va)

        fee_sa = withdraw_sa.times(Params.tx_fee_rate())
        self._fee_pool.deposit(fee_sa)

        vc_amount = services.get_adjusted_voucher_quantity(withdraw_steps_va)
        vc_denom = services.serialize_voucher_denom(self._oracle.get_price_of(self._va_denom))
        vc_tokens = types.Tokens(vc_amount, vc_denom)
        self._erc_tc.mint_to(buyer, vc_tokens)
        logger.info(Events.Buyer.SuccessBuy.fmt(buyer, tokens_va, withdraw_sa.amount))

    def process_buyer_redeem_request(self, buyer: types.AgentType, vc_tokens: types.Tokens):
        """
        Buyer Scenario - REDEEM

        Steps:
            1. (external) buyer sends voucher tokens to contract
            2. Calculate amount of VA that should be redeemed to buyer
            3. Burn voucher tokens (* this should be done AFTER Step 2 *)
            4. If there is nothing to redeem (DEFLATION or LOW BALANCE), re-mint vouchers to buyer for later use
            5. Redeem calculated amount of VA to buyer
            4. Extract Redemption Fee (Option Premium) and deposit to Fee Pool
        """
        logger.info(Events.Buyer.AttemptingRedeem.fmt(buyer, vc_tokens))
        redeem_usd = self._calculate_amount_to_redeem_buyer_usd(vc_tokens)
        self._erc_tc.burn(vc_tokens)

        if redeem_usd <= 0:
            self._erc_tc.mint_to(buyer, vc_tokens)
            return

        # assume that 1 SA <> 1 USD
        redeem_va = self._oracle.exchange(types.Tokens(redeem_usd, self._sa_denom), self._va_denom)

        redeem_usd_minus_fees = redeem_usd * (1 - Params.op_premium())
        redeem_va_minus_fees = redeem_va.times(1 - Params.op_premium())
        self._va_pool.redeem_to(buyer, redeem_va_minus_fees)

        fee_va = redeem_va.times(Params.op_premium())
        self._va_pool.withdraw(fee_va)
        fee_sa = self._oracle.exchange(fee_va, self._sa_denom)
        self._fee_pool.deposit(fee_sa)
        logger.info(Events.Buyer.SuccessRedeem.fmt(buyer, redeem_va_minus_fees, redeem_usd_minus_fees))

    def process_lp_provider_request(self, provider: types.AgentType, tokens_sa: types.Tokens):
        logger.info(Events.Provider.AttemptingProvide.fmt(provider, tokens_sa))
        self._sa_pool.deposit(tokens_sa, protocol_injected=provider.type == 'Protocol')
        amount_lp = self._sa_pool.calculate_lp_token_amount(tokens_sa)
        tokens_lp = types.Tokens(amount_lp, 'LP')
        self._lp_tc.mint_to(provider, tokens_lp)
        logger.info(Events.Provider.SuccessProvide.fmt(provider, tokens_sa))

    def process_lp_provider_redeem_request(self, provider: types.AgentType, tokens_lp: types.Tokens):
        logger.info(Events.Provider.AttemptingRedeem.fmt(provider, tokens_lp))
        lp_portion = self._lp_tc.calculate_lp_portion(tokens_lp)
        # NOTE: this must be done AFTER lp_portion is calculated
        self._lp_tc.burn(tokens_lp)

        # NOTE: assuming that initial liquidity is provided by the protocol
        # Otherwise, we will double count principal and initial liquidity
        redeem_principal_amount = (self._sa_pool.principal + self._sa_pool.initial_liquidity) * lp_portion
        redeem_sa = types.Tokens(redeem_principal_amount, self._sa_denom)

        # liquidate VA Pool if necessary, and redeem to provider
        self._handle(self._sa_pool.redeem_to, provider, redeem_sa)

        redeem_fee_usd = self._fee_pool.balance * lp_portion
        redeem_fee = types.Tokens(redeem_fee_usd, self._sa_denom)
        # redeem fees to provider
        self._fee_pool.redeem_to(provider, redeem_fee)

        logger.info(Events.Provider.SuccessRedeem.fmt(provider, redeem_sa.plus(redeem_fee)))

    def _handle(self, func, *args):
        """
        Handler for withdrawals from SA Pool.
        If there are not enough funds initially, this will attempt to liquidate VA Pool, then retry once.
        """
        result, e = func(*args)
        if isinstance(e, errors.PoolNotEnoughBalanceError):
            deficit = result
            liq_amount = self._oracle.exchange(deficit, self._va_denom)
            # logger.warning(events.AttemptingLiquidationEvent(liq_amount, 'NEED INJECTION'))
            self._va_pool.liquidate(liq_amount)
            self._sa_pool.deposit(deficit)
            result, e = func(*args)
            if e:
                raise e
        elif e:  # catch other errors
            raise e
        return result

    def _va_pool_value_usd(self) -> float:
        # price = self._oracle.get_price_of(self._va_denom)
        return self._bobs.va_pool_value_usd()

    def _target_va_pool_value_usd(self) -> float:
        return max(self._sa_pool.principal * Params.danger_threshold(), 0)

    def _calculate_amount_to_redeem_buyer_usd(self, vc_tokens: types.Tokens) -> float:
        cur_price = self._oracle.get_price_of(self._va_denom)

        # calculate the maximum rate of inflationary returns that can be redeemed to buyers
        r_m = InflationTracker.calculate_max_redeem_rate(self._erc_tc, cur_price, self._va_pool_value_usd(),
                                                         self._target_va_pool_value_usd())

        vc_amount, vc_denom = vc_tokens.decompose()
        og_price = services.deserialize_voucher_denom(vc_denom)

        # get inflation rate for the received voucher tokens
        inflation_rate = InflationTracker.calculate_inflation(og_price, cur_price)
        redeem_usd = og_price * vc_amount * inflation_rate * r_m

        if redeem_usd <= 0:
            event_prefix = 'DEFLATION' if inflation_rate <= 0 else 'LOW BALANCE' if r_m <= 0 else ''
            logger.warning(events.NothingToRedeemEvent(vc_tokens, event_prefix))

        return redeem_usd

    def _calculate_withdraw_steps(self, tokens_to_withdraw: types.Tokens) -> Tuple[List[types.Tokens], types.Tokens]:
        """
        Calculate amounts that are withdrawn at each level of the SA Pool.
        """
        n_floors: int = Params.n_floors()
        remaining_withdraw: float = tokens_to_withdraw.amount
        upper_floor: float = self._sa_pool.balance
        withdraw_steps: List[types.Tokens] = []

        for i in range(n_floors - 1, 0, -1):
            rate: float = i / n_floors
            current_floor: float = self._sa_pool.principal * rate
            if self._sa_pool.balance <= current_floor:
                continue
            upper_floor = min(upper_floor, self._sa_pool.balance)
            amount_in_range: float = upper_floor - current_floor
            # amount that can be withdrawn at that range
            withdraw_from_range: float = min(amount_in_range, remaining_withdraw)
            withdraw_steps.append(types.Tokens(withdraw_from_range, self._sa_denom))
            remaining_withdraw -= withdraw_from_range
            if remaining_withdraw == 0:
                break
            upper_floor = current_floor

        assert remaining_withdraw + sum([token.amount for token in withdraw_steps]) == tokens_to_withdraw.amount
        # remaining tokens are in DANGER level, and must be converted automatically
        return withdraw_steps, types.Tokens(remaining_withdraw, self._sa_denom)

    def _automated_conversion(self, tokens: types.Tokens):
        logger.info(Events.Router.AttemptingAutomatedConversion.fmt(tokens))
        # events.AutomatedTransferEvent(tokens))
        self._va_pool.liquidate(tokens)
