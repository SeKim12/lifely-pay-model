from typing import Dict
from collections import defaultdict
from decimal import Decimal

from states.interfaces import TokenI, WalletI, BuyerWalletI, AgentI
from utils.safe_decimals import gt, lt, leq


class DummyProtocolAgent(AgentI):
    @property
    def wallet(self):
        return Wallet("LifelyPay")

    def step(self):
        pass

    @property
    def name(self):
        return "LifelyPay"

    @property
    def type(self):
        return "Protocol"

    def receives(self, tokens: TokenI):
        return

    def sends(self, tokens: TokenI):
        return


class Tokens(TokenI):
    def __init__(self, amount: Decimal, denom: str):
        self._amount = amount
        self._denom = denom

    @property
    def amount(self):
        return self._amount

    @property
    def denom(self):
        return self._denom

    def decompose(self):
        return self._amount, self._denom

    def plus(self, token: TokenI):
        if token.denom != self._denom:
            raise Exception
        return Tokens(self._amount + token.amount, self._denom)

    def times(self, dec: Decimal):
        return Tokens(self._amount * dec, self._denom)

    def minus(self, token: TokenI):
        if token.denom != self._denom:
            raise Exception
        return Tokens(self._amount - token.amount, self._denom)

    def _set(self, amount: Decimal):
        self._amount = amount


class Wallet(WalletI):
    def __init__(self, owner: str):
        self._owner = owner
        self._funds = defaultdict(Decimal)

        self._total_spent = defaultdict(Decimal)
        self._total_redeemed = defaultdict(Decimal)

    @property
    def owner(self) -> str:
        return self._owner

    @property
    def funds(self) -> Dict[str, Decimal]:
        return self._funds

    @property
    def total_redeemed(self) -> Dict[str, Decimal]:
        return self._total_redeemed

    @property
    def total_spent(self) -> Dict[str, Decimal]:
        return self._total_spent

    def receives(self, tokens: TokenI):
        amount, denom = tokens.decompose()
        # track total amount of tokens redeemed
        self._total_redeemed[denom] += amount
        self._funds[denom] += amount

    def sends(self, tokens: TokenI):
        to_send, denom = tokens.decompose()
        if lt(self._funds[denom], to_send):
            raise Exception
        self._funds[denom] -= to_send
        # track total amount that was spent, either through staking or buying
        self._total_spent[denom] += to_send

    def balance_of(self, denom: str) -> Decimal:
        return self._funds[denom]


class BuyerWallet(Wallet, BuyerWalletI):
    def redeemable_balance(self, cur_price: Decimal):
        for denom in self._funds:
            if denom[0] == "<":
                og_price = Decimal(denom[1:-1].split("-")[1])
                if leq(og_price, cur_price) and self._funds[denom] != 0:
                    return Tokens(self._funds[denom], denom)
        return
