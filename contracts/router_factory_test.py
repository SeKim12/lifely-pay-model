# import unittest
# from unittest.mock import patch, PropertyMock
#
# from contracts import router_factory
# from utils import types, services, processlogger
# from states import errors
# from states.params import Params
#
# logger = processlogger.ProcessLogger()
#
#
# class TestRouterBuy(unittest.TestCase):
#     def setUp(self):
#         self.router = router_factory.Router()
#         self.protocol = types.DummyProtocolAgent()
#
#     def tearDown(self):
#         self.router._oracle.reset()
#
#     @patch('agents.buyer.BuyerAgent')
#     def test_process_buyer_buy_request_sufficient_usdc(self, mock_buyer):
#         type(mock_buyer).name = PropertyMock(return_value="Creed")
#         type(mock_buyer).identity = PropertyMock(return_value=("Buyer", "Creed"))
#
#         paid = types.Tokens(100, 'ETH')
#
#         self.router._sa_pool.deposit(types.Tokens(1000000, 'USDC'), protocol_injected=True)
#         self.router.process_buyer_buy_request(mock_buyer, paid)
#
#         paid_sa = self.router._oracle.exchange(paid, 'USDC')
#         paid_usd = paid_sa.amount
#
#         expected_fees = paid_sa.times(Params.tx_fee_rate()).amount
#         self.assertEqual(self.router._sa_pool.balance, 1000000 - paid_usd)
#         self.assertEqual(self.router._fee_pool.balance, expected_fees)
#         self.assertEqual(self.router._va_pool.balance, 100)
#
#         price = self.router._oracle.get_price_of('ETH')
#         vc = services.serialize_voucher_denom(price)
#
#         self.assertEqual(self.router._erc_tc.get_token_issued(vc), 100)
#         logger.test('#test_process_buyer_buy_request_sufficient_usdc()')
#
#     @patch('agents.buyer.BuyerAgent')
#     def test_process_buyer_buy_request_automated_conversion(self, mock_buyer):
#         type(mock_buyer).name = PropertyMock(return_value="Michael")
#         type(mock_buyer).identity = PropertyMock(return_value=("Buyer", "Michael"))
#
#         paid = types.Tokens(10, 'ETH')
#
#         self.router.process_buyer_buy_request(mock_buyer, paid)
#
#         paid_sa = self.router._oracle.exchange(paid, 'USDC')
#         expected_fees = paid_sa.times(Params.tx_fee_rate()).amount
#
#         self.assertEqual(self.router._sa_pool.balance, 0)
#         self.assertEqual(self.router._va_pool.balance, 0)
#         self.assertEqual(self.router._fee_pool.balance, expected_fees)
#
#         price = self.router._oracle.get_price_of('ETH')
#         vc = services.serialize_voucher_denom(price)
#
#         self.assertEqual(self.router._erc_tc.get_token_issued(vc), 0)
#         logger.test('#test_process_buyer_buy_request_automated_conversion()')
#
#     @patch('agents.buyer.BuyerAgent')
#     def test_process_buyer_redeem_request_sufficient_funds(self, mock_buyer):
#         type(mock_buyer).name = PropertyMock(return_value="Jim")
#         type(mock_buyer).identity = PropertyMock(return_value=("Buyer", "Jim"))
#
#         self.router._sa_pool.deposit(types.Tokens(10000000, 'USDC'), protocol_injected=True)
#
#         paid = types.Tokens(1, 'ETH')
#         self.router.process_buyer_buy_request(mock_buyer, paid)
#         fee_before_redeem = self.router._fee_pool.balance
#
#         self.router._oracle._force_change_price_to(2000, 'ETH')
#         denom = '<price-1337.0>'
#         vouchers = types.Tokens(1, denom)
#         self.router.process_buyer_redeem_request(mock_buyer, vouchers)
#
#         self.assertEqual(mock_buyer.receives.call_count, 2)
#         self.assertEqual(self.router._erc_tc.get_token_issued(denom), 0)
#         self.assertLess(self.router._va_pool.balance, 1)
#         self.assertGreater(self.router._fee_pool.balance, fee_before_redeem)
#         logger.test('#test_process_buyer_redeem_request_sufficient_funds()')
#
#     @patch('agents.buyer.BuyerAgent')
#     def test_process_buyer_redeem_request_low_balance(self, mock_buyer):
#         self.router._sa_pool.deposit(types.Tokens(2000, 'USDC'), protocol_injected=True)
#         self.router._sa_pool.deposit(types.Tokens(3000, 'USDC'), protocol_injected=False)
#
#         type(mock_buyer).name = PropertyMock(return_value="Pam")
#         type(mock_buyer).identity = PropertyMock(return_value=("Buyer", "Pam"))
#
#         self.router.process_buyer_buy_request(mock_buyer, types.Tokens(1, 'ETH'))
#         fee_before_redeem = self.router._fee_pool.balance
#
#         self.router._oracle._force_change_price_to(2000, 'ETH')
#         denom = '<price-1337.0>'
#         vouchers = types.Tokens(1, denom)
#         self.router.process_buyer_redeem_request(mock_buyer, vouchers)
#
#         self.assertEqual(self.router._erc_tc.get_token_issued(denom), 1)
#         self.assertEqual(self.router._fee_pool.balance, fee_before_redeem)
#         self.assertEqual(mock_buyer.receives.call_count, 2)
#         logger.test('#test_process_buyer_redeem_request_low_balance()')
#
#     @patch('agents.buyer.BuyerAgent')
#     def test_process_buyer_redeem_request_deflation(self, mock_buyer):
#         self.router._sa_pool.deposit(types.Tokens(1000000, 'USDC'), protocol_injected=True)
#
#         type(mock_buyer).name = PropertyMock(return_value="Toby")
#         type(mock_buyer).identity = PropertyMock(return_value=("Buyer", "Toby"))
#
#         self.router.process_buyer_buy_request(mock_buyer, types.Tokens(2, 'ETH'))
#         fee_before_redeem = self.router._fee_pool.balance
#
#         self.router._oracle._force_change_price_to(1000, 'ETH')
#         denom = '<price-1337.0>'
#         vouchers = types.Tokens(2, denom)
#         self.router.process_buyer_redeem_request(mock_buyer, vouchers)
#
#         self.assertEqual(self.router._erc_tc.get_token_issued(denom), 2)
#         self.assertEqual(self.router._va_pool.balance, 2)
#         self.assertEqual(self.router._fee_pool.balance, fee_before_redeem)
#         self.assertEqual(mock_buyer.receives.call_count, 2)
#         logger.test('#test_process_buyer_redeem_request_deflation()')
#
#
# class TestRouterProvider(unittest.TestCase):
#     def setUp(self):
#         self.router = router_factory.Router()
#         self.protocol = types.DummyProtocolAgent()
#
#     def tearDown(self):
#         self.router._oracle.reset()
#
#     def test_process_lp_provider_request_is_protocol(self):
#         self.router.process_lp_provider_request(self.protocol, types.Tokens(10000, 'USDC'))
#         # pool initialized with protocol injected liquidity
#         self.assertEqual(self.router._sa_pool.initial_liquidity, 10000)
#         self.assertEqual(self.router._sa_pool.balance, 10000)
#         # protocol injected liquidity does not affect principal
#         self.assertEqual(self.router._sa_pool.principal, 0)
#         # 1 LP token issued for initial amount, sets proportion for future liquidity providers
#         self.assertEqual(self.router._lp_tc.get_token_issued('LP'), 1)
#         logger.test('#test_process_lp_provider_request_is_protocol()')
#
#     @patch('agents.lp_provider.ProviderAgent')
#     def test_process_lp_provider_request(self, mock_provider):
#         type(mock_provider).name = PropertyMock(return_value="Kevin")
#         type(mock_provider).identity = PropertyMock(return_value=("Provider", "Kevin"))
#
#         init_liq = types.Tokens(1000, 'USDC')
#         self.router.process_lp_provider_request(self.protocol, init_liq)
#         provide = init_liq.times(0.5)
#         self.router.process_lp_provider_request(mock_provider, provide)
#
#         self.assertEqual(self.router._sa_pool.balance, 1500)
#         # protocol injected liquidity is not included in principal
#         self.assertEqual(self.router._sa_pool.principal, 500)
#         # initial liquidity does not change for future deposits
#         self.assertEqual(self.router._sa_pool.initial_liquidity, 1000)
#         # 1 LP for initial deposit ==> a deposit half that size == 0.5 LP
#         self.assertEqual(self.router._lp_tc.get_token_issued('LP'), 1.5)
#
#         # receives LP tokens (on deposit)
#         mock_provider.receives.assert_called_once()
#         logger.test('#test_process_lp_provider_request()')
#
#     @patch('agents.lp_provider.ProviderAgent')
#     def test_process_lp_provider_redeem_request(self, mock_provider):
#         type(mock_provider).name = PropertyMock(return_value="Angela")
#         type(mock_provider).identity = PropertyMock(return_value=("Provider", "Angela"))
#
#         init_liq = types.Tokens(1000, 'USDC')
#         self.router.process_lp_provider_request(self.protocol, init_liq)
#
#         self.router._fee_pool._balance = 600
#
#         provide = init_liq.times(0.5)
#         self.router.process_lp_provider_request(mock_provider, provide)
#         self.router.process_lp_provider_redeem_request(mock_provider, types.Tokens(0.5, 'LP'))
#
#         # provider redeemed principal
#         self.assertEqual(self.router._sa_pool.balance, 1000)
#         # provider took 1/3 of the fee pool, 2/3 remaining
#         self.assertEqual(self.router._fee_pool.balance, 400)
#         # 0.5 LP token burned
#         self.assertEqual(self.router._lp_tc.get_token_issued('LP'), 1)
#         # receive LP Token (on deposit), receive from SA Pool (on redeem), receive from Fee Pool (on redeem)
#         self.assertEqual(mock_provider.receives.call_count, 3)
#         logger.test('#test_process_lp_provider_redeem_request()')
#
#     @patch('agents.lp_provider.ProviderAgent')
#     def test_process_lp_provider_redeem_request_insufficient_usdc_pool(self, mock_provider):
#         type(mock_provider).name = PropertyMock(return_value="Kelly")
#         type(mock_provider).identity = PropertyMock(return_value=("Provider", "Kelly"))
#
#         init_liq = types.Tokens(100, 'USDC')
#         self.router.process_lp_provider_request(self.protocol, init_liq)
#
#         provide = init_liq.times(0.5)
#         self.router.process_lp_provider_request(mock_provider, provide)
#
#         # manually jack up VA Pool and drain SA Pool to test liquidation
#         self.router._va_pool._balance = 2
#         self.router._sa_pool._balance = 0
#
#         self.router.process_lp_provider_redeem_request(mock_provider, types.Tokens(0.5, 'LP'))
#
#         # provider redeemed principal
#         self.assertEqual(self.router._sa_pool.balance, 0)
#         # provider took 1/3 of the fee pool, 2/3 remaining
#         self.assertLess(self.router._va_pool.balance, 2)
#         # 0.5 LP token burned
#         self.assertEqual(self.router._lp_tc.get_token_issued('LP'), 1)
#         # receive LP Token (on deposit), receive from SA Pool (on redeem), receive from Fee Pool (on redeem)
#         self.assertEqual(mock_provider.receives.call_count, 3)
#         logger.test('#test_process_lp_provider_redeem_request_insufficient_usdc_pool()')
#
#     @patch('agents.lp_provider.ProviderAgent')
#     def test_process_lp_provider_redeem_request_insufficient_eth_pool(self, mock_provider):
#         type(mock_provider).name = PropertyMock(return_value="Andy")
#         type(mock_provider).identity = PropertyMock(return_value=("Provider", "Andy"))
#
#         self.router._sa_pool._principal = 1000
#         self.router._lp_tc._tokens_issued['LP'] = 1
#         with self.assertRaises(errors.CannotLiquidateEnoughError):
#             self.router.process_lp_provider_redeem_request(mock_provider, types.Tokens(1, 'LP'))
#
#         logger.test('#test_process_lp_provider_redeem_request_insufficient_eth_pool()')
#
#
# if __name__ == '__main__':
#     unittest.main()
