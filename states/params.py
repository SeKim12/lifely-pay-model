from decimal import Decimal

from utils import processlogger
from states import events

logger = processlogger.ProcessLogger()


class Params:
    _tolerance = Decimal("0.2")
    _content = Decimal("0.6")

    _tx_fee_rate = Decimal("0.02")
    _op_premium = Decimal("0.01")

    _danger_threshold = Decimal("1.15")

    _safety_floor = Decimal(3) / Decimal(4)

    _n_floors = Decimal(4)  # not including DANGER

    _safety_premium = Decimal(1)

    _n_premiums = Decimal(4)  # not including DANGER

    _redeem_cap = Decimal(1)

    _liquidation_spread = Decimal("0.10")

    _buy_cap = Decimal(100)  # ETH
    _stake_cap = Decimal(1000000)  # USDC

    @staticmethod
    def hard_reset():
        Params.tolerance(Decimal("0.2"))
        Params.content(Decimal("0.6"))
        Params.tx_fee_rate(Decimal("0.02"))
        Params.op_premium(Decimal("0.01"))
        Params.danger_threshold(Decimal("1.15"))
        Params.safety_floor(Decimal(3 / 4))
        Params.n_floors(Decimal(4))
        Params.safety_premium(Decimal(1))
        Params.redeem_cap(Decimal(1))
        Params.liquidation_spread(Decimal("0.10"))
        Params.buy_cap(Decimal(100))
        Params.stake_cap(Decimal(1000000))

    @staticmethod
    def buy_cap(set_val=None):
        if set_val:
            logger.info(events.ParamChangeEvent("Buy Cap", Params._buy_cap, set_val))
            Params._buy_cap = set_val
        return Params._buy_cap

    @staticmethod
    def stake_cap(set_val=None):
        if set_val:
            logger.info(
                events.ParamChangeEvent("Stake Cap", Params._stake_cap, set_val)
            )
            Params._stake_cap = set_val
        return Params._stake_cap

    @staticmethod
    def content(set_val=None):
        if set_val:
            logger.info(events.ParamChangeEvent("Content", Params._content, set_val))
            Params._content = set_val
        return Params._content

    @staticmethod
    def tolerance(set_val=None):
        if set_val:
            logger.info(
                events.ParamChangeEvent("Tolerance", Params._tolerance, set_val)
            )
            Params._tolerance = set_val
        return Params._tolerance

    @staticmethod
    def tx_fee_rate(set_val=None):
        if set_val:
            logger.info(
                events.ParamChangeEvent("Transaction Fee", Params._tx_fee_rate, set_val)
            )
            Params._tx_fee_rate = set_val
        return Params._tx_fee_rate

    @staticmethod
    def danger_threshold(set_val=None):
        if set_val:
            logger.info(
                events.ParamChangeEvent(
                    "Danger Threshold", Params._danger_threshold, set_val
                )
            )
            Params._danger_threshold = set_val
        return Params._danger_threshold

    @staticmethod
    def op_premium(set_val=None):
        if set_val:
            logger.info(
                events.ParamChangeEvent("Refund Fee", Params._op_premium, set_val)
            )
            Params._op_premium = set_val
        return Params._op_premium

    @staticmethod
    def safety_floor(set_val=None):
        if set_val:
            logger.info(
                events.ParamChangeEvent("Safety Floor", Params._safety_floor, set_val)
            )
            Params._safety_floor = set_val
        return Params._safety_floor

    @staticmethod
    def n_floors(set_val=None):
        if set_val:
            logger.info(
                events.ParamChangeEvent("Floor Step", Params._n_floors, set_val)
            )
            Params._n_floors = set_val
            Params._n_premiums = set_val
        return Params._n_floors

    @staticmethod
    def safety_premium(set_val=None):
        if set_val:
            logger.info(
                events.ParamChangeEvent(
                    "Safety Premium", Params._safety_premium, set_val
                )
            )
            Params._safety_premium = set_val
        return Params._safety_premium

    @staticmethod
    def redeem_cap(set_val=None):
        if set_val:
            logger.info(
                events.ParamChangeEvent("Redeem Cap", Params._redeem_cap, set_val)
            )
            Params._redeem_cap = set_val
        return Params._redeem_cap

    @staticmethod
    def liquidation_spread(set_val=None):
        if set_val:
            logger.info(
                events.ParamChangeEvent(
                    "Liquidation Spread", Params._liquidation_spread, set_val
                )
            )
            Params._liquidation_spread = set_val
        return Params._liquidation_spread

    # @staticmethod
    # def premium_step(set_val=None):
    #     if set_val:
    #         logger.info(events.ParamChangeEvent('Premium Step', Params._danger_threshold, set_val))
    #         Params._premium_step = set_val
    #         Params._floor_
    #     return Params._premium_step
