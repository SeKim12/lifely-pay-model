from utils import processlogger, types, services
from states.params import Params

logger = processlogger.ProcessLogger()


class InflationTracker:
    @staticmethod
    def calculate_inflation(og_price: float, cur_price: float) -> float:
        return max((cur_price / og_price) - 1.0, 0)

    @staticmethod
    def calculate_max_redeem_rate(erc_tc: types.TokenContractType, cur_price_usd: float, cur_balance_usd: float,
                                  target_balance_usd: float) -> float:
        surplus_balance_usd = max(cur_balance_usd - target_balance_usd, 0)
        inflation_pool_returns = InflationTracker._get_total_pool_returns_from_inflation_usd(erc_tc, cur_price_usd)
        if surplus_balance_usd <= 0 or inflation_pool_returns <= 0:
            return 0
        return min(surplus_balance_usd / inflation_pool_returns, Params.redeem_cap())

    @staticmethod
    def _get_total_pool_returns_from_inflation_usd(erc_tc: types.TokenContractType, cur_price_usd: float) -> float:
        returns_usd = 0
        for denom in erc_tc.tokens_issued:
            quantity_issued = erc_tc.get_token_issued(denom)
            og_price = services.deserialize_voucher_denom(denom)
            returns_usd += InflationTracker.calculate_inflation(og_price, cur_price_usd) * (og_price * quantity_issued)
        return returns_usd
