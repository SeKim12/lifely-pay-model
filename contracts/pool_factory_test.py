# import unittest
# from unittest.mock import patch, PropertyMock
#
# from agents import buyer
# from contracts import pool_factory
# from states import errors
# from utils import types, processlogger
#
# logger = processlogger.ProcessLogger()
#
#
# class TestStablePoolMethods(unittest.TestCase):
#     def setUp(self):
#         self.usdc_pool = pool_factory.StablePool('USDC')
#
#     def test_initial_liquidity(self):
#         self.assertEqual(self.usdc_pool.initial_liquidity, 0)
#         self.usdc_pool.deposit(types.Tokens(1000, 'USDC'), protocol_injected=True)
#         self.assertEqual(self.usdc_pool.initial_liquidity, 1000)
#         self.usdc_pool.deposit(types.Tokens(1000, 'USDC'))
#         self.assertEqual(self.usdc_pool.initial_liquidity, 1000)
#         logger.test('#test_initial_liquidity()')
#
#     def test_calculate_lp_token_amount(self):
#         provide = types.Tokens(100, 'USDC')
#         self.usdc_pool.deposit(provide)
#         amount_lp = self.usdc_pool.calculate_lp_token_amount(provide)
#         self.assertEqual(amount_lp, 1)
#
#         provide_2 = provide.times(0.5)
#         amount_lp_2 = self.usdc_pool.calculate_lp_token_amount(provide_2)
#         self.assertEqual(amount_lp_2, 0.5)
#         logger.test('#test_calculate_lp_token_amount()')
#
#     def test_denom(self):
#         self.assertEqual(self.usdc_pool.denom, 'USDC')
#         logger.test('#test_denom()')
#
#     def test_type(self):
#         self.assertEqual(self.usdc_pool.type, 'USDC')
#         logger.test('#test_type()')
#
#     def test_balance(self):
#         self.assertEqual(self.usdc_pool.balance, 0)
#         logger.test('#test_balace()')
#
#     def test_deposit(self):
#         tokens = types.Tokens(1000, 'USDC')
#         self.usdc_pool.deposit(tokens)
#         self.assertEqual(self.usdc_pool.balance, 1000)
#         self.assertEqual(self.usdc_pool.principal, 1000)
#         logger.test('#test_deposit()')
#
#     def test_deposit_by_protocol(self):
#         tokens = types.Tokens(1000, 'USDC')
#         self.usdc_pool.deposit(tokens, protocol_injected=True)
#         self.assertEqual(self.usdc_pool.balance, 1000)
#         self.assertEqual(self.usdc_pool.principal, 0)
#         logger.test('#test_deposit_by_protocol()')
#
#     def test_withdraw_success(self):
#         tokens_d = types.Tokens(10000, 'USDC')
#         self.usdc_pool.deposit(tokens_d)
#
#         tokens_w = tokens_d.times(0.5)
#         withdrawn, e = self.usdc_pool.withdraw(tokens_w)
#         self.assertEqual(withdrawn.amount, 5000)
#         self.assertEqual(self.usdc_pool.balance, 5000)
#         self.assertEqual(self.usdc_pool.principal, 10000)
#         self.assertIsNone(e)
#         logger.test('#test_withdraw_success()')
#
#     def test_withdraw_error(self):
#         tokens_d = types.Tokens(10000, 'USDC')
#         self.usdc_pool.deposit(tokens_d)
#
#         tokens_w = tokens_d.times(2)
#         deficit, e = self.usdc_pool.withdraw(tokens_w)
#         self.assertEqual(deficit.amount, 10000)
#         self.assertEqual(self.usdc_pool.balance, 10000)
#         self.assertEqual(self.usdc_pool.principal, 10000)
#         self.assertIsInstance(e, errors.PoolNotEnoughBalanceError)
#         logger.test('#test_withdraw_error()')
#
#     @patch('agents.buyer.BuyerAgent')
#     def test_redeem_to_success(self, mock_buyer):
#         assert mock_buyer is buyer.BuyerAgent
#         type(mock_buyer).identity = PropertyMock(return_value=('Buyer', 'Tom'))
#
#         tokens = types.Tokens(10000, 'USDC')
#         self.usdc_pool.deposit(tokens)
#
#         tokens_r = tokens.times(0.5)
#
#         redeemed, e = self.usdc_pool.redeem_to(mock_buyer, tokens_r)
#
#         self.assertEqual(redeemed.amount, 5000)
#         self.assertIsNone(e)
#
#         self.assertEqual(self.usdc_pool.balance, 5000)
#         self.assertEqual(self.usdc_pool.principal, 5000)
#         logger.test('#test_redeem_to_success()')
#
#     @patch('agents.buyer.BuyerAgent')
#     def test_redeem_to_error(self, mock_buyer):
#         type(mock_buyer).identity = PropertyMock(return_value=('Buyer', 'John'))
#         tokens = types.Tokens(10000, 'USDC')
#         self.usdc_pool.deposit(tokens)
#
#         tokens_r = tokens.times(2)
#
#         deficit, e = self.usdc_pool.redeem_to(mock_buyer, tokens_r)
#
#         self.assertEqual(deficit.amount, 10000)
#         self.assertIsInstance(e, errors.PoolNotEnoughBalanceError)
#
#         self.assertEqual(self.usdc_pool.balance, 10000)
#         self.assertEqual(self.usdc_pool.principal, 10000)
#         logger.test('#test_redeem_to_error()')
#
#     def test_enforce_denom(self):
#         wrong_tokens = types.Tokens(10000, 'ETH')
#         with self.assertRaises(errors.UnrecognizedDenomError):
#             self.usdc_pool.deposit(wrong_tokens)
#         logger.test('#test_enforce_denom()')
#
#     @patch('agents.buyer.BuyerAgent')
#     def test_transfer_to(self, mock_buyer):
#         type(mock_buyer).identity = PropertyMock(return_value=('Buyer', 'Timothy'))
#         tokens = types.Tokens(10000, 'USDC')
#         self.usdc_pool.deposit(tokens)
#
#         transfer = tokens.times(0.5)
#         self.usdc_pool._transfer_to(mock_buyer, transfer)
#
#         mock_buyer.receives.assert_called_once_with(transfer)
#         logger.test('#test_transfer_to()')
#
#
# class TestVolatilePoolMethods(unittest.TestCase):
#     def setUp(self):
#         self.eth_pool = pool_factory.VolatilePool('ETH')
#
#     def test_withdraw_error(self):
#         tokens_d = types.Tokens(1000, 'ETH')
#         self.eth_pool.deposit(tokens_d)
#         tokens_w = tokens_d.times(2)
#         with self.assertRaises(errors.PoolNotEnoughBalanceError):
#             self.eth_pool.withdraw(tokens_w)
#         logger.test('#test_withdraw_error()')
#
#     def test_liquidate_success(self):
#         tokens_d = types.Tokens(1000, 'ETH')
#         self.eth_pool.deposit(tokens_d)
#
#         tokens_l = tokens_d.times(0.5)
#         liquidated = self.eth_pool.liquidate(tokens_l)
#
#         self.assertEqual(self.eth_pool.balance, 500)
#         self.assertEqual(liquidated.amount, 500)
#         logger.test('#test_liquidate_success()')
#
#     def test_liquidate_error(self):
#         tokens_d = types.Tokens(1000, 'ETH')
#         self.eth_pool.deposit(tokens_d)
#
#         tokens_l = tokens_d.times(2)
#         with self.assertRaises(errors.CannotLiquidateEnoughError):
#             self.eth_pool.liquidate(tokens_l)
#
#         self.assertEqual(self.eth_pool.balance, 1000)
#         logger.test('#test_liquidate_error()')
#
#
# if __name__ == '__main__':
#     unittest.main()
