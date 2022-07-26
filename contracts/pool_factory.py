from decimal import Decimal

from states.errors import (
    PoolNotEnoughBalanceError,
    PoolNotInitializedError,
    UnrecognizedDenomError,
    CannotLiquidateEnoughError,
)
from states.events import Events
from states.interfaces import PoolI, StablePoolI, VolatilePoolI, TokenI, AgentI
from contracts.types import Tokens
from utils import processlogger
from utils.safe_decimals import gt, lt

logger = processlogger.ProcessLogger()


class Pool(PoolI):
    def __init__(self, denom: str):
        self._type = denom
        self._denom = denom
        self._balance = Decimal(0)

    @property
    def denom(self):
        return self._denom

    @property
    def type(self):
        return self._type

    @property
    def balance(self):
        return self._balance

    def deposit(self, tokens: TokenI, protocol_injected=False):
        """
        Deposit tokens to pool.

        :param protocol_injected: NOOP
        :param tokens: tokens to deposit, w/ same denom as pool
        :return: tokens deposited
        """
        amount, denom = tokens.decompose()
        self._enforce_denom(denom)
        self._balance += amount
        logger.debug(Events.Pool.DepositSuccess.fmt(self, tokens))
        return tokens

    def withdraw(self, tokens: TokenI):
        """
        Withdraw tokens from pool.
        Redeeming / liquidation MUST incorporate withdraw, and is separate from withdraw logic.
        When not enough balance to withdraw, returns the difference along with an error.
        This error can be propagated for retry (SA Pool) or raised immediately (VA Pool)

        :param tokens: tokens to withdraw, w/ same denom as pool
        :return: tokens withdrawn, or deficit along with error.
        """
        amount, denom = tokens.decompose()
        self._enforce_denom(denom)
        if lt(self._balance, amount):
            deficit = Tokens(amount - self._balance, denom)
            return deficit, PoolNotEnoughBalanceError(
                self._balance, amount, self._denom
            )
        self._balance -= amount
        logger.debug(Events.Pool.WithdrawSuccess.fmt(self, tokens))
        return tokens, None

    def redeem_to(self, recipient: AgentI, tokens_to_redeem: TokenI):
        """
        Redeem to individual.
        When not enough balance, returns the difference along with an error.

        :param recipient: agent to redeem to
        :param tokens_to_redeem: tokens to redeem to recipient
        :return: tokens redeemed, or deficit along with error
        """
        redeem_amount, denom = tokens_to_redeem.decompose()
        self._enforce_denom(denom)
        transferred, e = self._transfer_to(recipient, tokens_to_redeem)
        if e:
            deficit = transferred
            return deficit, e
        logger.debug(Events.Pool.SuccessRedeem.fmt(self, recipient, transferred))
        return transferred, None

    def _enforce_denom(self, denom: str):
        """Enforce that received tokens have same denomination as pool"""
        if denom != self._denom:
            raise UnrecognizedDenomError(denom, self._denom)
        return

    def _transfer_to(self, recipient: AgentI, tokens: TokenI):
        """Transfer to recipient that w/ wallet that satisfies WalletI with receives method."""
        withdrew, e = self.withdraw(tokens)
        if e:
            deficit = withdrew
            return deficit, e
        recipient.receives(withdrew)
        return withdrew, None


class StablePool(Pool, StablePoolI):
    def __init__(self, denom: str):
        super().__init__(denom)
        self._principal = Decimal(0)
        self._initial_liquidity = Decimal(0)

        self._initiated = False

    @property
    def initial_liquidity(self):
        return self._initial_liquidity

    @property
    def principal(self):
        return self._principal

    def deposit(self, tokens: TokenI, protocol_injected=False):
        """
        SA Pool must be initialized by protocol injected liquidity before any other logic.
        Tracks initial liquidity and principal, on top of normal deposit.

        :param tokens: tokens to deposit
        :param protocol_injected: if deposit was made by protocol
        :return: tokens deposited
        """
        if not self._initiated and not protocol_injected:
            raise PoolNotInitializedError(self.type)
        super().deposit(tokens)
        # initialize stable pool and set initial liquidity, for LP token reference
        # pool MUST BE initialized by protocol
        if not self._initiated and protocol_injected:
            self._initial_liquidity = tokens.amount
            logger.info(Events.Pool.Initialized.fmt(self, tokens))
            self._initiated = True
        # protocol injected liquidity is not included as principal (i.e. low priority redeem)
        self._principal += tokens.amount if not protocol_injected else 0
        return tokens

    def withdraw(self, tokens: TokenI):
        if not self._initiated:
            raise PoolNotInitializedError(self.type)
        return super().withdraw(tokens)

    def redeem_to(self, recipient: AgentI, tokens_to_redeem: TokenI):
        """
        Propagate error along with difference, so Router can handle error and retry again after liquidation
        """
        if not self._initiated:
            raise PoolNotInitializedError(self.type)
        redeemed, e = super().redeem_to(recipient, tokens_to_redeem)
        if e:
            deficit = redeemed
            return deficit, e
        self._principal -= redeemed.amount
        return redeemed, None

    def calculate_lp_token_amount(self, tokens_sa: TokenI):
        """
        Calculate ratio of deposited tokens to initial liquidity in order to issue LP tokens pro rata.

        :param tokens_sa: tokens deposited
        :return: amount of LP tokens to issue
        """
        return (
            tokens_sa.amount / self._initial_liquidity
            if not self._initial_liquidity.is_zero()
            else 1
        )


class VolatilePool(Pool, VolatilePoolI):
    def __init__(self, denom: str):
        super().__init__(denom)

    def withdraw(self, tokens: TokenI):
        """
        Raise error immediately, as VA Pool **should not** have any issue withdrawing.
        """
        withdrew, e = super().withdraw(tokens)
        if e:
            raise e
        return withdrew, None

    def liquidate(self, tokens: TokenI):
        """
        Liquidate tokens from pool, and raise error if not enough balance.
        Liquidation is similar to withdrawal, and does not handle the deposit afterwards.

        :param tokens: tokens to liquidate, w/ same denom as pool
        :return: liquidated amount
        """
        logger.warning(Events.Pool.AttemptingLiquidation.fmt(self, tokens))
        liq_amount, denom = tokens.decompose()
        self._enforce_denom(denom)

        if lt(self._balance, liq_amount):
            raise CannotLiquidateEnoughError(liq_amount, self._balance, self._denom)
        withdrew, _ = self.withdraw(tokens)  # error should be raised in withdraw
        logger.info(Events.Pool.SuccessLiquidation.fmt(self, tokens))
        return withdrew


class FeePool(Pool):
    def __init__(self, denom: str):
        super().__init__(denom)
        self._type = "Fee"

    def withdraw(self, tokens: TokenI):
        """
        Raise error immediately, as Fee Pool **should not** have any issue withdrawing.
        """
        withdrew, e = super().withdraw(tokens)
        if e:
            raise e
        return withdrew, None


if __name__ == "__main__":
    pass
