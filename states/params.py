from . import events
from utils import processlogger

logger = processlogger.ProcessLogger()


class Params:
    _tolerance = 0.2

    _tx_fee_rate = 0.2
    _op_premium = 0.1

    _danger_threshold = 1.5

    _safety_floor = 3 / 4

    _n_floors = 4  # not including DANGER

    _safety_premium = 1

    _n_premiums = 4  # not including DANGER

    _redeem_cap = 1

    _liquidation_spread = 0.2

    @staticmethod
    def tolerance(set_val=None):
        if set_val:
            logger.info(events.ParamChangeEvent('Tolerance', Params._tolerance, set_val))
            Params._tolerance = set_val
        return Params._tolerance

    @staticmethod
    def tx_fee_rate(set_val=None):
        if set_val:
            logger.info(events.ParamChangeEvent('Transaction Fee', Params._tx_fee_rate, set_val))
            Params._tx_fee_rate = set_val
        return Params._tx_fee_rate

    @staticmethod
    def danger_threshold(set_val=None):
        if set_val:
            logger.info(events.ParamChangeEvent('Danger Threshold', Params._danger_threshold, set_val))
            Params._danger_threshold = set_val
        return Params._danger_threshold

    @staticmethod
    def op_premium(set_val=None):
        if set_val:
            logger.info(events.ParamChangeEvent('Refund Fee', Params._op_premium, set_val))
            Params._op_premium = set_val
        return Params._op_premium

    @staticmethod
    def safety_floor(set_val=None):
        if set_val:
            logger.info(events.ParamChangeEvent('Safety Floor', Params._safety_floor, set_val))
            Params._safety_floor = set_val
        return Params._safety_floor

    @staticmethod
    def n_floors(set_val=None):
        if set_val:
            logger.info(events.ParamChangeEvent('Floor Step', Params._n_floors, set_val))
            Params._n_floors = set_val
            Params._n_premiums = set_val
        return Params._n_floors

    @staticmethod
    def safety_premium(set_val=None):
        if set_val:
            logger.info(events.ParamChangeEvent('Safety Premium', Params._safety_premium, set_val))
            Params._safety_premium = set_val
        return Params._safety_premium

    @staticmethod
    def redeem_cap(set_val=None):
        if set_val:
            logger.info(events.ParamChangeEvent('Redeem Cap', Params._redeem_cap, set_val))
            Params._redeem_cap = set_val
        return Params._redeem_cap

    @staticmethod
    def liquidation_spread(set_val=None):
        if set_val:
            logger.info(events.ParamChangeEvent('Liquidation Spread', Params._liquidation_spread, set_val))
            Params._liquidation_spread = set_val
        return Params._liquidation_spread

    # @staticmethod
    # def premium_step(set_val=None):
    #     if set_val:
    #         logger.info(events.ParamChangeEvent('Premium Step', Params._danger_threshold, set_val))
    #         Params._premium_step = set_val
    #         Params._floor_
    #     return Params._premium_step
