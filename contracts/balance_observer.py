from typing import List

from states import events
from states.params import Params
from states.events import Events
from utils import types, processlogger
from . import oracle

logger = processlogger.ProcessLogger()


class BalanceObserver(types.ObserverType):
    def __init__(self, va_pool: types.VolatilePoolType, sa_pool: types.StablePoolType, fee_pool: types.PoolType):
        super().__init__()
        self._oracle = oracle.Oracle()

        self._va_pool = va_pool
        self._sa_pool = sa_pool
        self._fee_pool = fee_pool

        self.__rebalancing = False

    def va_pool_value_usd(self) -> float:
        price = self._oracle.get_price_of(self._va_pool.denom)
        return self._va_pool.balance * price

    def target_va_pool_value_usd(self) -> float:
        return max(self._sa_pool.principal * Params.danger_threshold() - self._sa_pool.balance, 0)

    def total_assets_list_usd(self) -> List[float]:
        return [self.va_pool_value_usd(), self._sa_pool.balance, self._fee_pool.balance]

    def on_recv(self, event: types.EventBus) -> None:
        if self.__rebalancing or not any(
                [isinstance(event, Events.Pool.WithdrawSuccess), isinstance(event, Events.Pool.DepositSuccess)]):
            return
        self.__rebalancing = False
        assets_lst = self.total_assets_list_usd()
        assets_usd = sum(assets_lst)
        threshold = self._sa_pool.principal * Params.danger_threshold()
        if assets_usd < threshold:
            logger.warning(events.TriggerDangerProtocolEvent(assets_lst, threshold))
            self.__rebalancing = True
            self.__trigger_danger_protocol()

    def __trigger_danger_protocol(self) -> None:
        liq_va = types.Tokens(self._va_pool.balance, self._va_pool.denom)
        self._va_pool.liquidate(liq_va)
        deposit_va = liq_va.times(1 - Params.liquidation_spread())
        deposit_sa = self._oracle.exchange(deposit_va, self._sa_pool.denom)
        self._sa_pool.deposit(deposit_sa)
