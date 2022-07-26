import mesa
from decimal import Decimal

from utils import processlogger
from states.events import Events
from states.interfaces import TokenI
from contracts.types import Tokens
from utils.safe_decimals import dec


logger = processlogger.ProcessLogger()


class Oracle(mesa.Agent):
    _initial_prices = {"ETH": dec(1337), "USDC": dec(1)}
    _prices = {"ETH": dec(1337), "USDC": dec(1)}

    def __init__(self, model):
        super().__init__(-1, model)

    def step(self):
        """
        TODO: price modifying logic goes here
        """
        Oracle._prices = Oracle._initial_prices

    @staticmethod
    def set_price(val):
        Oracle._prices["ETH"] = val

    @staticmethod
    def get_price_of(denom: str) -> Decimal:
        return Oracle._prices[denom]

    @staticmethod
    def exchange(src_token: TokenI, target_denom: str) -> TokenI:
        src_amount, src_denom = src_token.decompose()
        relative_price = Oracle.get_price_of(src_denom) / Oracle.get_price_of(
            target_denom
        )
        return Tokens(src_amount * relative_price, target_denom)

    @staticmethod
    def reset() -> None:
        Oracle._prices = Oracle._initial_prices

    """
    Test Methods
    """

    @staticmethod
    def _force_change_price_to(price: Decimal, denom: str) -> None:
        logger.debug(
            Events.Test.ChangePrice.fmt(denom, Oracle.get_price_of(denom), price)
        )
        Oracle._prices[denom] = price
