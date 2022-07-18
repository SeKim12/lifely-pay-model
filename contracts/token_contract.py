from typing import Dict, Set

from utils import types, processlogger
from states import errors
from states.events import Events
from collections import defaultdict

logger = processlogger.ProcessLogger()


class TokenContract(types.TokenContractType):
    def __init__(self):
        self._tokens_issued = defaultdict(float)
        self._denoms = set()

    @property
    def tokens_issued(self) -> Dict[str, float]:
        return self._tokens_issued

    @property
    def denoms(self) -> Set[str]:
        return self._denoms

    def get_token_issued(self, denom):
        return self._tokens_issued[denom]

    def burn(self, tokens: types.Tokens):
        amount, denom = tokens.decompose()
        amount_issued = self.get_token_issued(denom)
        if denom not in self._denoms:
            raise errors.BurnWrongTokenError(denom)
        if amount_issued - amount < 0:
            raise errors.NegativeCirculatingSupplyError(amount_issued, amount, denom)
        self._tokens_issued[denom] -= amount
        logger.info(Events.TokenContract.Burned.fmt(tokens))
        return tokens

    def mint_to(self, recipient: types.AgentType, tokens: types.Tokens):
        amount, denom = tokens.decompose()
        self._tokens_issued[denom] += amount
        recipient.receives(tokens)
        logger.info(Events.TokenContract.Minted.fmt(tokens, recipient))
        return tokens


class LPTokenContract(TokenContract):
    def __init__(self):
        super().__init__()
        self._denoms.add('LP')


class ERC1155TokenContract(TokenContract):
    def __init__(self):
        super().__init__()

    def mint_to(self, recipient: types.AgentType, tokens: types.Tokens):
        _, denom = tokens.decompose()
        super().mint_to(recipient, tokens)
        self._denoms.add(denom)
