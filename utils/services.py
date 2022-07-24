from states import globals
from states.params import Params
from utils import types, processlogger

logger = processlogger.ProcessLogger()

#
# def describe(number, description):
#     logger.info('\n\n*******TEST SUITE {}: {}*******'.format(number, description))
#
#
# def it(number, description, override='TEST'):
#     logger.info('\n\n{} {}: {}\n======================\n'.format(override, number, description))
#
#
# def annotate(number, description, override='SUBTEST'):
#     logger.info('\n\n{} {}: {}\n---------------------'.format(override, number, description))
#

# if 1 ETH = 10 USD, and 1 USDC = 2 USD,
# then 1 ETH = 5 USDC and 1 USDC = 1/5 USD
# exchange(10, ETH, USDC) => 50, i.e. 10 ETH = 50 USDC
# def exchange(source_token: types.Tokens, target_denom):
#     source_amount, source_denom = source_token.decompose()
#     relative_price = globals.prices[source_denom] / globals.prices[target_denom]
#
# #     return types.Tokens(source_amount * relative_price, target_denom)
# #
#
# def inflation_rate(og_price, cur_price):
#     """
#     If inflated 50%, return 0.5
#     If deflation, return 0
#     """
#     return max((cur_price / og_price) - 1.0, 0)

#
# def serialize_voucher_denom(price: float) -> str:
#     return '<price-{}>'.format(price)
#
#
# def deserialize_voucher_denom(denom: str) -> float:
#     return float(denom[1:-1].split('-')[1])
#
#
# def get_adjusted_voucher_quantity(withdraw_steps_va):
#     q = 0
#     withdraw_amounts = [tokens.amount for tokens in withdraw_steps_va]
#     premium = Params.safety_premium()
#     step = Params.n_floors()
#     for wa in withdraw_amounts:
#         q += wa * premium
#         premium -= 1 / step
#     return q
