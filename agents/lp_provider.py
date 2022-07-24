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
        self._staked = False

    @property
    def name(self) -> str:
        return self._name

    @property
    def type(self) -> str:
        return self._type

    @property
    def wallet(self):
        return self._wallet

    def receives(self, tokens):
        self._wallet.receives(tokens)

    def sends(self, tokens):
        self._wallet.sends(tokens)

    # Agent instance is activated with 50% chance
    def step(self):
        if random.choice([True, True, False]):
            return

        # With 50% chance, Provider redeems instead of providing
        if self._staked and random.choice([True, False]):
            redeemable = self._wallet.balance_of("LP")
            if redeemable.is_zero():
                redeem = Tokens(redeemable, "LP")
                # redeem some portion of LP tokens
                redeem_lp = redeem.times(Decimal(random.random()))
                self.sends(redeem_lp)
                self._router.process_lp_provider_redeem_request(self, redeem_lp)
                return

        self._staked = True
        stake_amount = Decimal(random.uniform(0, float(Params.stake_cap())))
        stake_sa = Tokens(stake_amount, "USDC")
        # send USDC to pool
        self.sends(stake_sa)
        self._router.process_lp_provider_request(self, stake_sa)
