from utils import processlogger

logger = processlogger.ProcessLogger()


class PoolNotEnoughBalanceError(Exception):
    def __init__(self, balance, required, denom):
        message = 'NO BALANCE: Remaining: {:.2f} {}, Need: {:.2f} {}'.format(balance, denom, required, denom)
        logger.critical(message)
        super().__init__(message)


class CannotLiquidateEnoughError(Exception):
    def __init__(self, liq_amount, actual_amount, denom):
        message = 'ASSET DEPLETED: Need to liquidate {} {}, Only have {} {}'.format(liq_amount, denom,
                                                                                            actual_amount, denom)
        logger.critical(message)
        super().__init__(message)


class UnrecognizedDenomError(Exception):
    def __init__(self, recv_denom, req_denom):
        message = 'UNRECOGNIZED DENOM: {} Pool Received Unrecognized Denom {}'.format(req_denom, recv_denom)
        logger.critical(message)
        super().__init__(message)


class BurnWrongTokenError(Exception):
    def __init__(self, recv_denom):
        message = 'WRONG TOKEN: {} Tokens were never issued; cannot be burned'.format(recv_denom)
        logger.critical(message)
        super().__init__(message)


class NegativeCirculatingSupplyError(Exception):
    def __init__(self, amount_issued, amount_burned, denom):
        message = 'NEGATIVE CIRCULATING SUPPLY: Attempting to burn {:.2f} {}, but only {:.2f} {} should be circulating' \
            .format(amount_burned, denom, amount_issued, denom)
        logger.critical(message)
        super().__init__(message)


class PoolNotInitializedError(Exception):
    def __init__(self, pool_type):
        message = 'NOT INITIALIZED: {} Pool Not Initialized. Protocol must inject liquidity first'.format(pool_type)
        logger.critical(message)
        super().__init__(message)
