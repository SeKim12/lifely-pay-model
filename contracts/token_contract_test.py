import unittest
from unittest.mock import patch, PropertyMock

import token_contract
from utils import types, processlogger
from states import errors

logger = processlogger.ProcessLogger()


class TestLPTokenContract(unittest.TestCase):
    def setUp(self):
        self.lp_tc = token_contract.LPTokenContract()

    @patch('agents.buyer.BuyerAgent')
    def test_mint_to(self, mock_staker):
        type(mock_staker).identity = PropertyMock(return_value=('Staker', 'Harry'))
        mint = types.Tokens(1000, 'LP')
        self.lp_tc.mint_to(mock_staker, mint)
        self.assertEqual(self.lp_tc.get_token_issued('LP'), 1000)
        mock_staker.receives.assert_called_once_with(mint)
        logger.test('#test_mint_to()')

    @patch('agents.buyer.BuyerAgent')
    def test_burn_success(self, mock_staker):
        type(mock_staker).identity = PropertyMock(return_value=('Staker', 'Hermione'))
        mint = types.Tokens(1000, 'LP')
        burn = mint.times(0.5)
        self.lp_tc.mint_to(mock_staker, mint)
        self.lp_tc.burn(burn)
        self.assertEqual(self.lp_tc.get_token_issued('LP'), 500)
        logger.test('#test_burn_success()')

    @patch('agents.buyer.BuyerAgent')
    def test_burn_error(self, mock_staker):
        type(mock_staker).identity = PropertyMock(return_value=('Staker', 'Ron'))
        mint = types.Tokens(1000, 'LP')
        self.lp_tc.mint_to(mock_staker, mint)
        burn = mint.times(2)
        with self.assertRaises(errors.NegativeCirculatingSupplyError):
            self.lp_tc.burn(burn)

        with self.assertRaises(errors.BurnWrongTokenError):
            self.lp_tc.burn(types.Tokens(50, 'JKROWLING'))

        self.assertEqual(self.lp_tc.get_token_issued('LP'), 1000)
        logger.test('#test_burn_error()')


class TestERC1155TokenContract(unittest.TestCase):
    def setUp(self):
        self.erc_tc = token_contract.ERC1155TokenContract()

    @patch('agents.buyer.BuyerAgent')
    def test_mint_to(self, mock_staker):
        type(mock_staker).identity = PropertyMock(return_value=('Staker', 'Dumbledore'))
        self.erc_tc.mint_to(mock_staker, types.Tokens(50, '<price-100.00>'))
        self.assertEqual(self.erc_tc.get_token_issued('<price-100.00>'), 50)
        self.assertEqual(self.erc_tc.get_token_issued('price-100.01'), 0)

        self.assertIn('<price-100.00>', self.erc_tc._denoms)
        self.assertNotIn('<price-100.01>', self.erc_tc._denoms)
        logger.test('#test_mint_to()')


if __name__ == '__main__':
    unittest.main()
