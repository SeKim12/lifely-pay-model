import unittest
from unittest.mock import patch, PropertyMock

from contracts import router_factory
from utils import types, services, processlogger
from states.params import Params

logger = processlogger.ProcessLogger()


class TestRouterBuy(unittest.TestCase):
    def setUp(self):
        self.router = router_factory.Router()

    def tearDown(self):
        self.router._oracle._reset_price_to_init()

    @patch('agents.buyer.BuyerAgent')
    def test_process_buyer_buy_request_sufficient_usdc(self, mock_buyer):
        type(mock_buyer).name = PropertyMock(return_value="Creed")
        type(mock_buyer).identity = PropertyMock(return_value=("Buyer", "Creed"))

        paid = types.Tokens(100, 'ETH')

        self.router._sa_pool.deposit(types.Tokens(1000000, 'USDC'), protocol_injected=True)
        self.router.process_buyer_buy_request(mock_buyer, paid)

        paid_sa = self.router._oracle.exchange(paid, 'USDC')
        paid_usd = paid_sa.amount

        expected_fees = paid_sa.times(Params.tx_fee_rate()).amount
        self.assertEqual(self.router._sa_pool.balance, 1000000 - paid_usd)
        self.assertEqual(self.router._fee_pool.balance, expected_fees)
        self.assertEqual(self.router._va_pool.balance, 100)

        price = self.router._oracle.get_price_of('ETH')
        vc = services.serialize_voucher_denom(price)

        self.assertEqual(self.router._erc_tc.get_token_issued(vc), 100)
        logger.test('#test_process_buyer_buy_request_sufficient_usdc()')

    @patch('agents.buyer.BuyerAgent')
    def test_process_buyer_buy_request_automated_conversion(self, mock_buyer):
        type(mock_buyer).name = PropertyMock(return_value="Michael")
        type(mock_buyer).identity = PropertyMock(return_value=("Buyer", "Michael"))

        paid = types.Tokens(10, 'ETH')

        self.router.process_buyer_buy_request(mock_buyer, paid)

        paid_sa = self.router._oracle.exchange(paid, 'USDC')
        expected_fees = paid_sa.times(Params.tx_fee_rate()).amount

        self.assertEqual(self.router._sa_pool.balance, 0)
        self.assertEqual(self.router._va_pool.balance, 0)
        self.assertEqual(self.router._fee_pool.balance, expected_fees)

        price = self.router._oracle.get_price_of('ETH')
        vc = services.serialize_voucher_denom(price)

        self.assertEqual(self.router._erc_tc.get_token_issued(vc), 0)
        logger.test('#test_process_buyer_buy_request_automated_conversion()')

    @patch('agents.buyer.BuyerAgent')
    def test_process_buyer_redeem_request_sufficient_funds(self, mock_buyer):
        type(mock_buyer).name = PropertyMock(return_value="Jim")
        type(mock_buyer).identity = PropertyMock(return_value=("Buyer", "Jim"))

        self.router._sa_pool.deposit(types.Tokens(10000000, 'USDC'), protocol_injected=True)

        paid = types.Tokens(1, 'ETH')
        self.router.process_buyer_buy_request(mock_buyer, paid)
        fee_before_redeem = self.router._fee_pool.balance

        self.router._oracle._force_change_price_to(2000, 'ETH')
        denom = '<price-1337.0>'
        vouchers = types.Tokens(1, denom)
        self.router.process_buyer_redeem_request(mock_buyer, vouchers)

        self.assertEqual(mock_buyer.receives.call_count, 2)
        self.assertEqual(self.router._erc_tc.get_token_issued(denom), 0)
        self.assertLess(self.router._va_pool.balance, 1)
        self.assertGreater(self.router._fee_pool.balance, fee_before_redeem)
        logger.test('#test_process_buyer_redeem_request_sufficient_funds()')

    @patch('agents.buyer.BuyerAgent')
    def test_process_buyer_redeem_request_low_balance(self, mock_buyer):
        self.router._sa_pool.deposit(types.Tokens(2000, 'USDC'), protocol_injected=True)
        self.router._sa_pool.deposit(types.Tokens(3000, 'USDC'), protocol_injected=False)

        type(mock_buyer).name = PropertyMock(return_value="Pam")
        type(mock_buyer).identity = PropertyMock(return_value=("Buyer", "Pam"))

        self.router.process_buyer_buy_request(mock_buyer, types.Tokens(1, 'ETH'))
        fee_before_redeem = self.router._fee_pool.balance

        self.router._oracle._force_change_price_to(2000, 'ETH')
        denom = '<price-1337.0>'
        vouchers = types.Tokens(1, denom)
        self.router.process_buyer_redeem_request(mock_buyer, vouchers)

        self.assertEqual(self.router._erc_tc.get_token_issued(denom), 1)
        self.assertEqual(self.router._fee_pool.balance, fee_before_redeem)
        self.assertEqual(mock_buyer.receives.call_count, 2)
        logger.test('#test_process_buyer_redeem_request_low_balance()')

    @patch('agents.buyer.BuyerAgent')
    def test_process_buyer_redeem_request_deflation(self, mock_buyer):
        self.router._sa_pool.deposit(types.Tokens(1000000, 'USDC'), protocol_injected=True)

        type(mock_buyer).name = PropertyMock(return_value="Toby")
        type(mock_buyer).identity = PropertyMock(return_value=("Buyer", "Toby"))

        self.router.process_buyer_buy_request(mock_buyer, types.Tokens(2, 'ETH'))
        fee_before_redeem = self.router._fee_pool.balance

        self.router._oracle._force_change_price_to(1000, 'ETH')
        denom = '<price-1337.0>'
        vouchers = types.Tokens(2, denom)
        self.router.process_buyer_redeem_request(mock_buyer, vouchers)

        self.assertEqual(self.router._erc_tc.get_token_issued(denom), 2)
        self.assertEqual(self.router._va_pool.balance, 2)
        self.assertEqual(self.router._fee_pool.balance, fee_before_redeem)
        self.assertEqual(mock_buyer.receives.call_count, 2)
        logger.test('#test_process_buyer_redeem_request_deflation()')


if __name__ == '__main__':
    unittest.main()
