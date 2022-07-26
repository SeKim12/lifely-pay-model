import mesa
import random
from decimal import Decimal

from states.params import Params
from states.interfaces import WalletI, RouterI, AgentI

from contracts.types import Wallet, Tokens


class ProviderAgent(mesa.Agent, AgentI):
    def __init__(self, unique_id: int, name: str, router: RouterI, model):
        super().__init__(unique_id, model)
        self._name = name
        self._wallet = Wallet(name)
        self._type = "Provider"
        self._router = router

        # NOP
        self.spent_eth_usd = Decimal("nan")
        self.redeemed_eth_usd = Decimal("nan")
        self.remaining_vouchers = Decimal("nan")

        # Used in model
        self._staked = False
        self.staked_usd = Decimal(0)
        self.redeemed_usd = Decimal(0)

    def initiate_with(self, denom):
        self._wallet.initiate_with(denom)

    @property
    def name(self) -> str:
        return self._name

    @property
    def type(self) -> str:
        return self._type

    @property
    def wallet(self):
        return self._wallet

    @property
    def apy(self):
        redeemable = self._router.dry_run_redeem_lp(
            Tokens(self._wallet.balance_of("LP"), "LP")
        )
        if self.staked_usd.is_zero():
            return Decimal(0)
        apy = (((self.redeemed_usd + redeemable) / self.staked_usd) - 1) * 100
        return apy

    def receives(self, tokens):
        if tokens.denom == "USDC":
            self.redeemed_usd += tokens.amount
        self._wallet.receives(tokens)

    def sends(self, tokens):
        if tokens.denom == "USDC":
            self.staked_usd += tokens.amount
        self._wallet.sends(tokens)

    # Agent instance is activated with 50% chance
    def step(self):
        # With 50% chance, Provider redeems instead of providing
        if self._staked:
            if random.choice([True, False]):
                redeemable = self._wallet.balance_of("LP")
                if not redeemable.is_zero():
                    redeem = Tokens(redeemable, "LP")
                    # redeem some portion of LP tokens
                    redeem_lp = redeem.times(Decimal(random.random()))
                    self.sends(redeem_lp)
                    self._router.process_lp_provider_redeem_request(self, redeem_lp)
        if not self._router.is_accepting_liquidity:
            return
        if random.choice([True, False]):
            return
        self._staked = True
        stake_amount = Decimal(random.uniform(0, float(Params.stake_cap())))
        stake_sa = Tokens(stake_amount, "USDC")
        # send USDC to pool
        self.sends(stake_sa)
        self._router.process_lp_provider_request(self, stake_sa)
