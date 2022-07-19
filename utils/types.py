from abc import ABCMeta, abstractmethod
from collections import defaultdict
from typing import Tuple, Dict, Set
from typing_extensions import TypeAlias

from states import errors

Exception_: TypeAlias = Exception or None


class Wallet:
    def __init__(self, owner: str):
        self._owner = owner
        self._funds = defaultdict(float)

    @property
    def owner(self) -> str:
        return self._owner

    @property
    def funds(self) -> Dict[str, float]:
        return self._funds

    def receives(self, tokens):
        amount, denom = tokens.decompose()
        self._funds[denom] += amount
        return self

    def sends(self, tokens):
        to_send, denom = tokens.decompose()
        if self._funds[denom] < to_send:
            raise Exception
        self._funds[denom] -= to_send
        return self

    def balance_of(self, denom) -> float:
        return self._funds[denom]


class EventBus:
    def fmt(self, *args, **kwargs) -> str:
        pass


class Tokens:
    def __init__(self, amount, denom):
        self._amount: float = amount
        self._denom: str = denom

    @property
    def amount(self):
        return self._amount

    @property
    def denom(self):
        return self._denom

    def decompose(self):
        return self._amount, self._denom

    def plus(self, token):
        if token.denom != self._denom:
            raise Exception
        return Tokens(self._amount + token.amount, self._denom)

    def times(self, dec):
        return Tokens(self._amount * dec, self._denom)

    def _set(self, amount):
        self._amount = amount


class AgentType(metaclass=ABCMeta):

    @property
    @abstractmethod
    def identity(self) -> Tuple[str, str]:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def type(self) -> str:
        pass

    # @abstractmethod
    # def get_name(self):
    #     pass
    #
    # @abstractmethod
    # def get_wallet(self):
    #     pass
    #
    # @abstractmethod
    # def get_type(self):
    #     pass

    @abstractmethod
    def receives(self, tokens: Tokens):
        pass

    @abstractmethod
    def sends(self, tokens: Tokens):
        pass


class DummyProtocolAgent(AgentType):

    @property
    def identity(self) -> Tuple[str, str]:
        return 'Protocol', 'LifelyPay'

    @property
    def name(self) -> str:
        return 'LifelyPay'

    @property
    def type(self) -> str:
        return 'Protocol'

    def receives(self, tokens: Tokens):
        return

    def sends(self, tokens: Tokens):
        return


class ObserverType(metaclass=ABCMeta):
    @abstractmethod
    def on_recv(self, event: EventBus):
        pass


class PoolType(metaclass=ABCMeta):
    @property
    @abstractmethod
    def type(self) -> str:
        pass

    @property
    @abstractmethod
    def denom(self) -> str:
        pass

    @property
    @abstractmethod
    def balance(self) -> float:
        pass

    @abstractmethod
    def deposit(self, tokens: Tokens) -> Tokens:
        pass

    @abstractmethod
    def withdraw(self, tokens: Tokens) -> Tuple[Tokens, Exception_]:
        pass

    @abstractmethod
    def redeem_to(self, recipient: AgentType, tokens: Tokens) -> Tuple[Tokens, Exception_]:
        pass


class StablePoolType(PoolType):
    @property
    @abstractmethod
    def principal(self) -> float:
        pass

    @property
    @abstractmethod
    def initial_liquidity(self) -> float:
        pass

    @abstractmethod
    def calculate_lp_token_amount(self, tokens_sa: Tokens) -> float:
        pass


class VolatilePoolType(PoolType):
    @abstractmethod
    def liquidate(self, tokens: Tokens) -> Tokens:
        pass


class TokenContractType(metaclass=ABCMeta):

    @property
    @abstractmethod
    def tokens_issued(self) -> Dict[str, float]:
        pass

    @property
    @abstractmethod
    def denoms(self) -> Set[str]:
        pass

    @abstractmethod
    def get_token_issued(self, denom: str) -> float:
        pass

    @abstractmethod
    def burn(self, tokens: Tokens):
        pass

    @abstractmethod
    def mint_to(self, recipient: AgentType, tokens: Tokens):
        pass
