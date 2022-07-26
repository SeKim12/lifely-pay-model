from typing import List, Tuple
from decimal import Decimal
from math import isclose

from contracts.types import Tokens
from states.params import Params
from states.events import Events
from states.interfaces import BalanceTrackerI, PoolI, VolatilePoolI, StablePoolI, TokenI
from utils import processlogger
from utils.safe_decimals import leq
from agents.oracle import Oracle

logger = processlogger.ProcessLogger()


class BalanceTracker(BalanceTrackerI):
    def __init__(self, va_pool: VolatilePoolI, sa_pool: StablePoolI, fee_pool: PoolI):
        self._va_pool = va_pool
        self._sa_pool = sa_pool
        self._fee_pool = fee_pool

        self._warning = False
        self._count = 200

        # Used for model
        self.num_triggered = 0
        self.num_rebalanced = 0

    @property
    def warning(self):
        return self._warning

    def va_pool_value_usd(self) -> Decimal:
        price = Oracle.get_price_of(self._va_pool.denom)
        return self._va_pool.balance * price

    def target_va_pool_value_usd(self) -> Decimal:
        """
        The MINIMUM USD value of the VA Pool for the protocol's total asset value to be exactly at threshold,
        where threshold == principal * theta for some predefined parameter theta (init 1.15)
        """
        return max(
            self._sa_pool.principal - self._sa_pool.balance - self._fee_pool.balance,
            Decimal(0),
        )

    def get_withdraw_amount_per_range(
        self, withdraw_sa: TokenI
    ) -> Tuple[List[TokenI], TokenI]:
        n_floors = int(Params.n_floors())
        remaining = withdraw_sa.amount

        ceiling = self._sa_pool.balance
        steps = []

        for i in range(n_floors - 1, 0, -1):
            # Ensure that length is the same for all withdraw steps
            if leq(remaining, 0):
                steps.append(Tokens(Decimal(0), self._sa_pool.denom))
                continue
            floor = self._sa_pool.principal * Decimal(i / n_floors)
            if leq(self._sa_pool.balance, floor):
                steps.append(Tokens(Decimal(0), self._sa_pool.denom))
                continue

            ceiling = min(ceiling, self._sa_pool.balance)

            balance_in_range = ceiling - floor
            withdraw_from_range = min(balance_in_range, remaining)
            steps.append(Tokens(withdraw_from_range, self._sa_pool.denom))

            remaining -= withdraw_from_range
            ceiling = floor

        assert isclose(sum([t.amount for t in steps]) + remaining, withdraw_sa.amount)

        return steps, Tokens(remaining, self._sa_pool.denom)

    def rebalance(self) -> None:
        """
        Pool Rebalancing occurs in one of two scenarios:
            1. When Emergency Protocol is triggered (everything is liquidated)
            2. When USDC Pool is considered dry (even though total asset value is not depleted)

        Once Emergency Protocol is triggered, the protocol is considered to be in warning state.
        In warning state, buyer redemptions will be turned off, and all payments will be automatically converted.
        The warning state will only trigger back on once USDC pool value reaches content level.

        For the model, the rebalance method is called at the end of every e2e router transaction.
        In practice, polling would have to occur much more frequently (and probably done off-chain)
        """
        target_va_price_usd = (
            self.target_va_pool_value_usd() / self._va_pool.balance
            if not self._va_pool.balance.is_zero()
            else Decimal(0)
        )

        actual_va_price_usd = Oracle.get_price_of(self._va_pool.denom)

        tolerant_level = self._sa_pool.principal * Params.tolerance()
        content_level = self._sa_pool.principal * Params.content()
        threshold = Decimal("1.1111111")

        # Case 1 (EMERGENCY): Convert all remaining VA to SA =>
        #   when actual price of VA <= target price of VA,
        #   set protocol balance to WARNING, and start count
        #   protocol blocks any withdrawal from SA Pool until count,
        #   then resumes iff protocol balances are stabilized

        # liquidation spread == 10%, need to liquidate at 11.1111...% to get 100% principal
        if not self._warning and leq(
            actual_va_price_usd, target_va_price_usd * threshold
        ):
            self.num_triggered += 1
            self._warning = True
            self._count = 200
            logger.warning(
                Events.Balancer.TriggerEmergencyProtocol.fmt(
                    self._total_assets_list_usd(),
                    self._sa_pool.principal,
                    actual_va_price_usd,
                    target_va_price_usd,
                )
            )
            return self._trigger_danger_protocol()

        # Case 2: Refill USDC pool =>
        #   even when total asset value is stable, the SA pool may be deficient
        #   this would cause frequent liquidations for payments and LP redemptions, etc.
        #   therefore, when SA pool balance falls below a certain parameter,
        #   we refill the pool up to a pre-determined sufficient amount
        elif leq(self._sa_pool.balance, tolerant_level):
            self.num_rebalanced += 1
            logger.warning(
                Events.Balancer.Rebalacing.fmt(
                    self._sa_pool.balance, tolerant_level, content_level
                )
            )

            can_liquidate_va = Tokens(self._va_pool.balance, "ETH")
            can_liquidate_sa = Oracle.exchange(can_liquidate_va, "USDC")

            to_refill_sa = Tokens(
                min(can_liquidate_sa.amount, content_level - self._sa_pool.balance),
                "USDC",
            )

            to_refill_va = Oracle.exchange(to_refill_sa, "ETH")

            self._va_pool.liquidate(to_refill_va)
            self._sa_pool.deposit(to_refill_sa, protocol_injected=True)

            return

        # Case 3: Protocol is stable again =>
        #   when warning is turned on (i.e. buyer rewards are turned off),
        #   but protocol balances are stabilized (negation of trigger condition),
        #   then turn off warning iff mandatory count since trigger has been reached
        elif self._warning and actual_va_price_usd > target_va_price_usd * threshold:
            self._warning = self._count > 0
        self._count -= 1

    def _total_assets_list_usd(self) -> List[Decimal]:
        return [self.va_pool_value_usd(), self._sa_pool.balance, self._fee_pool.balance]

    def _trigger_danger_protocol(self) -> None:
        """
        Liquidates EVERYTHING in VA Pool and Fee Pool to SA Pool.
        Cash in VA Pool and the Fee Pool to SA Pool.
        """
        liq_va = Tokens(self._va_pool.balance, self._va_pool.denom)
        self._va_pool.liquidate(liq_va)
        # sell assets at a discount as incentive
        deposit_va = liq_va.times(1 - Params.liquidation_spread())
        deposit_sa = Oracle.exchange(deposit_va, self._sa_pool.denom)
        self._sa_pool.deposit(deposit_sa, protocol_injected=True)

        # total_fees = Tokens(self._fee_pool.balance, "USDC")
        # self._fee_pool.withdraw(total_fees)
        # self._sa_pool.deposit(total_fees, protocol_injected=True)
