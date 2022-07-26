import mesa
import random
from decimal import Decimal

from states.params import Params

from states.interfaces import AgentI, RouterI
from contracts.types import BuyerWallet, Tokens

from agents.oracle import Oracle


class BuyerAgent(mesa.Agent, AgentI):
    def __init__(self, unique_id: int, name: str, router: RouterI, model):
        super().__init__(unique_id, model)

        self._name = name
        self._wallet = BuyerWallet(name)
        self._type = "Buyer"
        self._router = router

        # NOP
        self.staked_usd = Decimal("nan")
        self.redeemed_usd = Decimal("nan")
        self.apy = Decimal("nan")

        # Used in model
        self._bought = False

        self.spent_eth_usd = Decimal(0)
        self.redeemed_eth_usd = Decimal(0)
        self.remaining_vouchers = Decimal(0)

    def initiate_with(self, denom):
        self._wallet.initiate_with(denom)

    def reached_buying_cap(self):
        return self.spent_eth_usd > 1000

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
        if tokens.denom[0] == "<":
            self.remaining_vouchers += tokens.amount
        if tokens.denom == "ETH":
            self.redeemed_eth_usd += tokens.amount * Oracle.get_price_of("ETH")
        self._wallet.receives(tokens)

    def sends(self, tokens):
        if tokens.denom[0] == "<":
            self.remaining_vouchers -= tokens.amount
        if tokens.denom == "ETH":
            self.spent_eth_usd += tokens.amount * Oracle.get_price_of("ETH")
        self._wallet.sends(tokens)

    # Agent is activated with 50% chance
    def step(self):
        price = Oracle.get_price_of("ETH")

        # With 50% chance (and if applicable), Buyer redeems instead of buying
        if self._bought:
            if random.choice([True, False]):
                redeemable = self._wallet.redeemable_balance(price)
                if redeemable:
                    # redeem some portion of VC tokens
                    redeem_vc = redeemable.times(Decimal(random.random()))
                    self.sends(redeem_vc)
                    self._router.process_buyer_redeem_request(self, redeem_vc)
        if random.choice([True, False]) or self.reached_buying_cap():
            return
        self._bought = True
        buy_amount = Decimal(random.uniform(0, float(Params.buy_cap())))
        buy_va = Tokens(buy_amount, "ETH")
        # send ETH to pool
        self.sends(buy_va)
        self._router.process_buyer_buy_request(self, buy_va)
