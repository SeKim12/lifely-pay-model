import unittest
from unittest.mock import patch

from contracts import pool_factory, balance_observer
from states.params import Params
from utils import types, processlogger

logger = processlogger.ProcessLogger()


class TestBalanceObserver(unittest.TestCase):
    def setUp(self):
        self.va_pool = pool_factory.VolatilePool('ETH')
        self.sa_pool = pool_factory.StablePool('USDC')
        self.fee_pool = pool_factory.FeePool('USDC')

        self.balancer = balance_observer.BalanceObserver(self.va_pool, self.sa_pool, self.fee_pool)
        self.va_pool.add_observer(self.balancer)
        self.sa_pool.add_observer(self.balancer)
        self.fee_pool.add_observer(self.balancer)

    def tearDown(self) -> None:
        self.balancer._oracle._reset_price_to_init()

    def test_va_pool_value_usd(self):
        self.balancer._oracle._force_change_price_to(1000, 'ETH')
        self.va_pool.deposit(types.Tokens(10, 'ETH'))
        self.assertEqual(self.balancer.va_pool_value_usd(), 10000)
        logger.test('#test_va_pool_value_usd()')

    def test_target_va_pool_value_usd(self):
        self.balancer._oracle._force_change_price_to(1000, 'ETH')
        self.sa_pool.deposit(types.Tokens(1000, 'USDC'), protocol_injected=False)
        self.va_pool.deposit(types.Tokens(10, 'ETH'))
        self.assertGreater(self.va_pool.balance * 1000, self.balancer.target_va_pool_value_usd())
        logger.test('#test_target_va_pool_value_usd()')

    def test_total_assets_list_usd(self):
        self.assertEqual(len(self.balancer.total_assets_list_usd()), 3)
        logger.test('#test_total_assets_list_usd()')

    @patch('contracts.balance_observer.BalanceObserver.on_recv')
    def test_on_recv_callback_works(self, on_recv_mock):
        self.va_pool.deposit(types.Tokens(100, 'ETH'))
        on_recv_mock.assert_called_once()
        logger.test('#test_on_recv_callback_works()')

    def test_trigger_danger_protocol(self):
        self.sa_pool._principal = 100
        sa = 100 * Params.danger_threshold() - 10
        tokens_va = self.balancer._oracle.exchange(types.Tokens(sa, 'USDC'), 'ETH')

        self.va_pool.deposit(tokens_va)
        logger.test('#test_trigger_danger_protocol()')


if __name__ == '__main__':
    unittest.main()
