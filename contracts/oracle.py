# from utils import processlogger, types
# from states.events import Events
#
# logger = processlogger.ProcessLogger()
#
#
# class Oracle:
#
#     def __init__(self, init_prices=None):
#         self.__init_fixed = {'ETH': 1337.0, 'USDC': 1.0}
#
#         self._prices = init_prices or self.__init_fixed
#         self._price_history = []
#
#     def get_price_of(self, denom: str) -> float:
#         return self._prices[denom]
#
#     def exchange(self, src_token: types.Tokens, target_denom: str) -> types.Tokens:
#         """
#         Exchange SRC Tokens to Tokens with denomination target_denom
#         """
#         src_amount, src_denom = src_token.decompose()
#         relative_price = self.get_price_of(src_denom) / self.get_price_of(target_denom)
#
#         return types.Tokens(src_amount * relative_price, target_denom)
#
#     def step(self):
#         pass
#
#     """
#     ==========Debug Functions==========
#     """
#
#     def _force_change_price_to(self, price: float, denom: str) -> None:
#         logger.debug(Events.Test.ChangePrice.fmt(denom, self.get_price_of(denom), price))
#         self._prices[denom] = price
#
#     def _reset_price_to_init(self) -> None:
#         self._prices = self.__init_fixed
