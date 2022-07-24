# from abc import ABCMeta, abstractmethod
# from collections import defaultdict
# from typing import Tuple, Dict, Set
# from typing_extensions import TypeAlias
#
# from states.interfaces import TokenI
#
# Exception_: TypeAlias = Exception or None
#
#
# #
# # class Tokens(TokenI):
# #
# #     def __init__(self, amount, denom):
# #         self._amount: float = amount
# #         self._denom: str = denom
# #
# #     @property
# #     def amount(self):
# #         return self._amount
# #
# #     @property
# #     def denom(self):
# #         return self._denom
# #
# #     def decompose(self):
# #         return self._amount, self._denom
# #
# #     def plus(self, token):
# #         if token.denom != self._denom:
# #             raise Exception
# #         return Tokens(self._amount + token.amount, self._denom)
# #
# #     def times(self, dec):
# #         return Tokens(self._amount * dec, self._denom)
# #
# #     def minus(self, token):
# #         if token.denom != self._denom:
# #             raise Exception
# #         return Tokens(self._amount - token.amount, self._denom)
# #
# #     def _set(self, amount):
# #         self._amount = amount
#
#
# # class Wallet:
# #     def __init__(self, owner: str):
# #         self._owner = owner
# #         self._funds = defaultdict(float)
# #
# #         self._total_spent = defaultdict(float)
# #         self._total_redeemed = defaultdict(float)
# #
# #     @property
# #     def owner(self) -> str:
# #         return self._owner
# #
# #     @property
# #     def funds(self) -> Dict[str, float]:
# #         return self._funds
# #
# #     @property
# #     def total_redeemed(self) -> Dict[str, float]:
# #         return self._total_redeemed
# #
# #     @property
# #     def total_spent(self) -> Dict[str, float]:
# #         return self._total_spent
# #
# #     def receives(self, tokens):
# #         amount, denom = tokens.decompose()
# #         # track total amount of tokens redeemed
# #         self._total_redeemed[denom] += amount
# #         self._funds[denom] += amount
# #         return self
# #
# #     def sends(self, tokens):
# #         to_send, denom = tokens.decompose()
# #         if self._funds[denom] < to_send:
# #             raise Exception
# #         self._funds[denom] -= to_send
# #         # track total amount that was spent, either through staking or buying
# #         self._total_spent[denom] += to_send
# #         return self
# #
# #     def balance_of(self, denom) -> float:
# #         return self._funds[denom]
# #
# #     def redeemable_balance(self, cur_price) -> Tokens or None:
# #         """
# #         BUYER WALLET ONLY
# #         Calculates tokens that can be redeemed at current price
# #         """
# #         for denom in self._funds:
# #             if denom[0] == '<':
# #                 og_price = float(denom[1:-1].split('-')[1])
# #                 if og_price <= cur_price and self._funds[denom] != 0:
# #                     return Tokens(self._funds[denom], denom)
# #         return
#
#
# class EventBus:
#     def fmt(self, *args, **kwargs) -> str:
#         pass
#
#
# class AgentType(metaclass=ABCMeta):
#
#     @property
#     @abstractmethod
#     def identity(self) -> Tuple[str, str]:
#         pass
#
#     @property
#     @abstractmethod
#     def name(self) -> str:
#         pass
#
#     @property
#     @abstractmethod
#     def type(self) -> str:
#         pass
#
#     @abstractmethod
#     def receives(self, tokens: Tokens):
#         pass
#
#     @abstractmethod
#     def sends(self, tokens: Tokens):
#         pass
#
#
# class ObserverType(metaclass=ABCMeta):
#     @abstractmethod
#     def on_recv(self, event: EventBus):
#         pass
#
#
# class PoolType(metaclass=ABCMeta):
#     @property
#     @abstractmethod
#     def type(self) -> str:
#         pass
#
#     @property
#     @abstractmethod
#     def denom(self) -> str:
#         pass
#
#     @property
#     @abstractmethod
#     def balance(self) -> float:
#         pass
#
#     @abstractmethod
#     def deposit(self, tokens: Tokens) -> Tokens:
#         pass
#
#     @abstractmethod
#     def withdraw(self, tokens: Tokens) -> Tuple[Tokens, Exception_]:
#         pass
#
#     @abstractmethod
#     def redeem_to(self, recipient: AgentType, tokens: Tokens) -> Tuple[Tokens, Exception_]:
#         pass
#
#
# class StablePoolType(PoolType):
#     @property
#     @abstractmethod
#     def principal(self) -> float:
#         pass
#
#     @property
#     @abstractmethod
#     def initial_liquidity(self) -> float:
#         pass
#
#     @abstractmethod
#     def calculate_lp_token_amount(self, tokens_sa: Tokens) -> float:
#         pass
#
#
# class VolatilePoolType(PoolType):
#     @abstractmethod
#     def liquidate(self, tokens: Tokens) -> Tokens:
#         pass
#
#
# class TokenContractType(metaclass=ABCMeta):
#
#     @property
#     @abstractmethod
#     def tokens_issued(self) -> Dict[str, float]:
#         pass
#
#     @property
#     @abstractmethod
#     def denoms(self) -> Set[str]:
#         pass
#
#     @abstractmethod
#     def get_token_issued(self, denom: str) -> float:
#         pass
#
#     @abstractmethod
#     def burn(self, tokens: Tokens):
#         pass
#
#     @abstractmethod
#     def mint_to(self, recipient: AgentType, tokens: Tokens):
#         pass
