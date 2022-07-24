import mesa
import random
from decimal import Decimal

from states.params import Params

from states.interfaces import AgentI, RouterI
from contracts.types import BuyerWallet, Tokens
from utils.safe_decimals import dec

from agents.oracle import Oracle


class BuyerAgent(mesa.Agent, AgentI):
    def __init__(self, unique_id: int, name: str, router: RouterI, model):
        super().__init__(unique_id, model)

        self._name = name
        self._wallet = BuyerWallet(name)
        self._type = "Buyer"
        self._router = router
        self._bought = False

    @property
    def name(self):
        return self._name

    @property
    def type(self):
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
        if random.choice([True, False, False]):
            return
        price = Oracle.get_price_of("ETH")

        # With 50% chance (and if applicable), Buyer redeems instead of buying
        if self._bought and random.choice([True, False]):
            redeemable = self._wallet.redeemable_balance(price)
            if redeemable:
                # redeem some portion of VC tokens
                redeem_vc = redeemable.times(Decimal(random.random()))
                self.sends(redeem_vc)
                self._router.process_buyer_redeem_request(self, redeem_vc)
                return

        self._bought = True
        buy_amount = Decimal(random.uniform(0, float(Params.buy_cap())))
        buy_va = Tokens(buy_amount, "ETH")
        # send ETH to pool
        self.sends(buy_va)
        self._router.process_buyer_buy_request(self, buy_va)
