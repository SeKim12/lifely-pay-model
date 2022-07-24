from typing import List
from decimal import Decimal

from utils import processlogger
from utils.safe_decimals import dec, lt, gt
from states import errors
from states.errors import NegativeCirculatingSupplyError, BurnWrongTokenError
from states.events import Events
from states.params import Params
from states.interfaces import TokenI, TokenContractI, AgentI, ERCTokenContractI
from collections import defaultdict

logger = processlogger.ProcessLogger()


class TokenContract(TokenContractI):
    def __init__(self):
        self._tokens_issued = defaultdict(Decimal)
        self._denoms = set()

    @property
    def tokens_issued(self):
        return self._tokens_issued

    @property
    def denoms(self):
        return self._denoms

    def get_token_issued(self, denom):
        return self._tokens_issued[denom]

    def burn(self, tokens: TokenI):
        amount, denom = tokens.decompose()
        amount_issued = self.get_token_issued(denom)
        if denom not in self._denoms:
            raise BurnWrongTokenError(denom)
        if lt(amount_issued - amount, 0):
            raise NegativeCirculatingSupplyError(amount_issued, amount, denom)
        self._tokens_issued[denom] -= amount
        logger.info(Events.TokenContract.Burned.fmt(tokens))
        return tokens

    def mint_to(self, recipient: AgentI, tokens: TokenI):
        amount, denom = tokens.decompose()
        self._tokens_issued[denom] += amount
        recipient.receives(tokens)
        logger.info(Events.TokenContract.Minted.fmt(tokens, recipient))
        return tokens


class LPTokenContract(TokenContract):
    def __init__(self):
        super().__init__()
        self._denoms.add("LP")

    def calculate_lp_portion(self, tokens_lp: TokenI):
        return tokens_lp.amount / self.get_token_issued("LP")


class ERC1155TokenContract(TokenContract, ERCTokenContractI):
    def __init__(self):
        super().__init__()

    @staticmethod
    def balance_adjusted_voucher_quantity(steps_va: List[TokenI]) -> Decimal:
        q = Decimal(0)
        withdraw_amounts = [t.amount for t in steps_va]
        premium = Params.safety_premium()
        step = Params.n_floors()
        for wa in withdraw_amounts:
            q += wa * premium
            premium -= 1 / step
        return q

    @staticmethod
    def serialize_vouchers(price: Decimal) -> str:
        return "<price-{}>".format(price)

    @staticmethod
    def deserialize_vouchers(denom: str) -> Decimal:
        return dec(denom[1:-1].split("-")[1])

    def mint_to(self, recipient: AgentI, tokens: TokenI):
        _, denom = tokens.decompose()
        super().mint_to(recipient, tokens)
        self._denoms.add(denom)
