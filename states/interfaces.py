from abc import ABCMeta, abstractmethod
from typing import Tuple, Dict, Set, Optional
from decimal import Decimal


class TokenI(metaclass=ABCMeta):
    @property
    @abstractmethod
    def amount(self) -> Decimal:
        pass

    @property
    @abstractmethod
    def denom(self) -> str:
        pass

    @abstractmethod
    def decompose(self) -> Tuple[Decimal, str]:
        pass

    @abstractmethod
    def plus(self, token: 'TokenI') -> 'TokenI':
        pass

    @abstractmethod
    def minus(self, token: 'TokenI') -> 'TokenI':
        pass

    @abstractmethod
    def times(self, dec: Decimal) -> 'TokenI':
        pass


class WalletI(metaclass=ABCMeta):
    @property
    @abstractmethod
    def owner(self) -> str:
        pass

    @property
    @abstractmethod
    def funds(self) -> Dict[str, Decimal]:
        pass

    @abstractmethod
    def receives(self, tokens: TokenI) -> None:
        pass

    @abstractmethod
    def sends(self, tokens: TokenI) -> None:
        pass

    @abstractmethod
    def balance_of(self, denom: str) -> Decimal:
        pass

    @property
    @abstractmethod
    def total_redeemed(self) -> Dict[str, Decimal]:
        pass

    @property
    @abstractmethod
    def total_spent(self) -> Dict[str, Decimal]:
        pass


class BuyerWalletI(WalletI):
    @abstractmethod
    def redeemable_balance(self, cur_price: Decimal) -> Optional[TokenI]:
        pass


class EventBusI(metaclass=ABCMeta):
    @abstractmethod
    def fmt(self, *args, **kwargs) -> str:
        pass


class AgentI(metaclass=ABCMeta):

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def type(self) -> str:
        pass

    @property
    @abstractmethod
    def wallet(self) -> WalletI:
        pass

    @abstractmethod
    def receives(self, tokens: TokenI) -> None:
        pass

    @abstractmethod
    def sends(self, tokens: TokenI) -> None:
        pass

    @abstractmethod
    def step(self) -> None:
        pass


class PoolI(metaclass=ABCMeta):
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
    def balance(self) -> Decimal:
        pass

    @abstractmethod
    def deposit(self, tokens: TokenI) -> TokenI:
        pass

    @abstractmethod
    def withdraw(self, tokens: TokenI) -> Tuple[TokenI, Optional[Exception]]:
        pass

    @abstractmethod
    def redeem_to(self, recipient: AgentI, tokens: TokenI) -> Tuple[TokenI, Optional[Exception]]:
        pass


class StablePoolI(PoolI):
    @property
    @abstractmethod
    def principal(self) -> Decimal:
        pass

    @property
    @abstractmethod
    def initial_liquidity(self) -> Decimal:
        pass

    @abstractmethod
    def calculate_lp_token_amount(self, tokens: TokenI) -> Decimal:
        pass


class VolatilePoolI(PoolI):
    @abstractmethod
    def liquidate(self, tokens: TokenI) -> TokenI:
        pass


class TokenContractI(metaclass=ABCMeta):

    @property
    @abstractmethod
    def tokens_issued(self) -> Dict[str, Decimal]:
        pass

    @property
    @abstractmethod
    def denoms(self) -> Set[str]:
        pass

    @abstractmethod
    def get_token_issued(self, denom: str) -> Decimal:
        pass

    @abstractmethod
    def burn(self, tokens: TokenI) -> TokenI:
        pass

    @abstractmethod
    def mint_to(self, recipient: AgentI, tokens: TokenI) -> TokenI:
        pass


class ERCTokenContractI(TokenContractI):
    @staticmethod
    @abstractmethod
    def serialize_vouchers(price: Decimal) -> str:
        pass

    @staticmethod
    @abstractmethod
    def deserialize_vouchers(denom: str) -> Decimal:
        pass


class RouterI(metaclass=ABCMeta):
    @property
    @abstractmethod
    def va_denom(self) -> str:
        pass

    @property
    @abstractmethod
    def sa_denom(self) -> str:
        pass

    @abstractmethod
    def process_buyer_buy_request(self, buyer: AgentI, tokens: TokenI) -> None:
        pass

    @abstractmethod
    def process_buyer_redeem_request(self, buyer: AgentI, tokens: TokenI) -> None:
        pass

    @abstractmethod
    def process_lp_provider_request(self, provider: AgentI, tokens: TokenI) -> None:
        pass

    @abstractmethod
    def process_lp_provider_redeem_request(self, provider: AgentI, tokens: TokenI) -> None:
        pass


class BalanceTrackerI(metaclass=ABCMeta):
    @property
    @abstractmethod
    def warning(self) -> bool:
        pass

    @abstractmethod
    def rebalance(self) -> None:
        pass

    @abstractmethod
    def va_pool_value_usd(self) -> Decimal:
        pass

    @abstractmethod
    def target_va_pool_value_usd(self) -> Decimal:
        pass
