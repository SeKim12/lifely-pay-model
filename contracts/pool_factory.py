from states import errors
from states.events import Events
from utils import types, processlogger

logger = processlogger.ProcessLogger()


class Pool(types.PoolType):
    def __init__(self, base_denom: str):
        self._type = base_denom
        self._denom = base_denom
        self._balance = 0

        self._observers = []

    def add_observer(self, observer: types.ObserverType):
        self._observers.append(observer)

    @property
    def denom(self):
        return self._denom

    @property
    def type(self):
        return self._type

    @property
    def balance(self):
        return self._balance

    def deposit(self, tokens: types.Tokens):
        amount, denom = tokens.decompose()
        self._enforce_denom(denom)
        self._balance += amount

        logger.info(Events.Pool.DepositSuccess.fmt(self, tokens))
        self._fire_event(Events.Pool.DepositSuccess())
        return tokens

    def withdraw(self, tokens: types.Tokens):
        amount, denom = tokens.decompose()
        self._enforce_denom(denom)

        if self._balance < amount:
            deficit = types.Tokens(amount - self._balance, denom)
            return deficit, errors.PoolNotEnoughBalanceError(self._balance, amount, self._denom)
        self._balance -= amount

        logger.info(Events.Pool.WithdrawSuccess.fmt(self, tokens))
        self._fire_event(Events.Pool.WithdrawSuccess())
        return tokens, None

    def redeem_to(self, recipient: types.AgentType, tokens_to_redeem: types.Tokens):
        redeem_amount, denom = tokens_to_redeem.decompose()
        self._enforce_denom(denom)

        transferred, e = self._transfer_to(recipient, tokens_to_redeem)
        if e:
            deficit = transferred
            return deficit, e

        logger.info(Events.Pool.SuccessRedeem.fmt(self, recipient, transferred))
        self._fire_event(Events.Pool.SuccessRedeem())
        return transferred, None

    def _enforce_denom(self, denom: str):
        if denom != self._denom:
            raise errors.UnrecognizedDenomError(denom, self._denom)
        return

    def _transfer_to(self, recipient: types.AgentType, tokens: types.Tokens):
        withdrew, e = self.withdraw(tokens)
        if e:
            deficit = withdrew
            return deficit, e
        recipient.receives(withdrew)
        return withdrew, None

    def _fire_event(self, event_type: types.EventBus):
        for observer in self._observers:
            observer.on_recv(event_type)


class StablePool(Pool, types.StablePoolType):
    def __init__(self, base_denom: str):
        super().__init__(base_denom)
        self._principal = 0
        self._initial_liquidity = 0

    @property
    def initial_liquidity(self):
        return self._initial_liquidity

    @property
    def principal(self):
        return self._principal

    def deposit(self, tokens: types.Tokens, protocol_injected=False):
        super().deposit(tokens)
        if self._initial_liquidity == 0:
            self._initial_liquidity = tokens.amount
            logger.info(Events.Pool.Initalized.fmt(self, tokens))
        self._initial_liquidity = self._initial_liquidity or tokens.amount
        self._principal += tokens.amount if not protocol_injected else 0
        return tokens

    def redeem_to(self, recipient: types.AgentType, tokens_to_redeem: types.Tokens):
        redeemed, e = (super().redeem_to(recipient, tokens_to_redeem))
        if e:
            deficit = redeemed
            return deficit, e
        self._principal -= redeemed.amount
        return redeemed, None

    def calculate_lp_token_amount(self, tokens_sa: types.Tokens):
        return tokens_sa.amount / self._initial_liquidity if self._initial_liquidity else 1


class VolatilePool(Pool, types.VolatilePoolType):
    def __init__(self, base_denom: str):
        super().__init__(base_denom)

    def withdraw(self, tokens: types.Tokens):
        """
        Volatile Pool **should** not have any issue withdrawing.
        Therefore, don't return, but raise Exception
        """
        withdrew, e = super().withdraw(tokens)
        if e:
            raise e
        return withdrew, None

    def liquidate(self, tokens: types.Tokens):
        """
        Liquidate required amount from Pool
        Note that pre-, post-conversion and deposit is external to contract,
        """
        logger.warning(Events.Pool.AttemptingLiquidation.fmt(self, tokens))
        liq_amount, denom = tokens.decompose()
        self._enforce_denom(denom)

        if self._balance < liq_amount:
            raise errors.CannotLiquidateEnoughError(liq_amount, self._balance, self._denom)
        withdrew, _ = self.withdraw(tokens)  # error is raised in withdraw
        logger.info(Events.Pool.SuccessLiquidation.fmt(self, tokens))
        return withdrew


class FeePool(Pool):
    def __init__(self, base_denom):
        super().__init__(base_denom)
        self._type = 'Fee'

    def withdraw(self, tokens: types.Tokens):
        """
        Fee Pool should not have any problem withdrawing.
        Therefore, raise Error
        """
        withdrew, e = super().withdraw(tokens)
        if e:
            raise e
        return withdrew, None


if __name__ == '__main__':
    pass
