from decimal import Decimal

from utils import processlogger
from utils.safe_decimals import leq, geq
from agents.oracle import Oracle
from states.params import Params
from states.interfaces import BalanceTrackerI, ERCTokenContractI

logger = processlogger.ProcessLogger()


class InflationTracker:
    def __init__(self, erc_tc: ERCTokenContractI, bt: BalanceTrackerI):
        self._erc_tc = erc_tc
        self._bt = bt

    @staticmethod
    def calculate_inflation(og_price: Decimal) -> Decimal:
        """
        Rate of inflation for asset, given original price

        :param og_price: original price of the asset
        :return: inflation rate
        """
        return max((Oracle.get_price_of("ETH") / og_price) - Decimal(1), Decimal(0))

    def calculate_max_redeem_rate(self) -> Decimal:
        """
        Calculates max redeem rate for buyers, accounting for inflation and current VA Pool value.

        :return: actual rate of the VA pool that can be redeemed (0 if no inflation or no surplus)
        """
        surplus_balance_usd = max(
            self._bt.va_pool_value_usd() - self._bt.target_va_pool_value_usd(),
            Decimal(0),
        )
        inflation_pool_returns = self._get_total_pool_returns_from_inflation_usd()
        if leq(surplus_balance_usd, 0) or leq(inflation_pool_returns, 0):
            return Decimal(0)

        return min(surplus_balance_usd / inflation_pool_returns, Params.redeem_cap())

    def _get_total_pool_returns_from_inflation_usd(self) -> Decimal:
        """
        For all VA tokens deposited (counted by vouchers issued),
        calculate accrued inflation returns for each price range.

        :return: inflation returns
        """
        returns_usd = Decimal(0)
        for denom in self._erc_tc.tokens_issued:
            quantity_issued = self._erc_tc.get_token_issued(denom)
            og_price = self._erc_tc.deserialize_vouchers(denom)
            returns_usd += self.calculate_inflation(og_price) * (
                og_price * quantity_issued
            )
        return returns_usd
