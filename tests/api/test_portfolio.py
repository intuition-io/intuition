'''
Tests for intuition.api.portfolio
'''

import unittest
from nose.tools import raises, ok_, eq_
import intuition.api.portfolio as portfolio
import intuition.test_utils as test_utils


class PortfolioUtilsTestCase(unittest.TestCase):

    def test__remove_useless_orders_empty_orders(self):
        allocation = {}
        new_allocation = portfolio._remove_useless_orders(allocation)
        eq_(new_allocation, {})

    def test__remove_useless_orders_nothing_to_do(self):
        allocation = {'goog': 34, 'aapl': -134}
        new_allocation = portfolio._remove_useless_orders(allocation)
        eq_(new_allocation, allocation)

    def test__remove_useless_orders(self):
        allocation = {'goog': 34, 'aapl': -134, 'useless': 0, 'also': -0}
        new_allocation = portfolio._remove_useless_orders(allocation)
        allocation.pop('useless')
        allocation.pop('also')
        eq_(new_allocation, allocation)


class PortfolioTestCase(unittest.TestCase):

    def setUp(self):
        test_utils.setup_logger(self)
        self.test_config = {'useless': 'parameter'}
        self.pf = test_utils.TestPortfolio(self.test_config)

    def tearDown(self):
        test_utils.teardown_logger(self)

    def test_new_portfolio(self):
        ok_(hasattr(self.pf, 'log'))
        self.assertIsNone(self.pf.date)
        self.assertIsNone(self.pf.perfs)
        self.assertIsNone(self.pf.portfolio)

    def test_overload_initialize(self):
        ok_(self.pf.initialized)

    def test_portfolio_config(self):
        eq_(self.pf._optimizer_parameters, self.test_config)

    def test_advise_portfolio(self):
        eq_(self.pf._optimizer_parameters, self.test_config)
        self.pf.advise(
            test=True, profile='fearless', favorites=['goog', 'aapl'])
        self.test_config.update({
            'test': True,
            'profile': 'fearless',
            'favorites': ['goog', 'aapl']
        })
        eq_(self.pf._optimizer_parameters, self.test_config)

    def test_update_portfolio_state(self):
        self.assertIsNone(self.pf.date)
        self.assertIsNone(self.pf.perfs)
        self.assertIsNone(self.pf.portfolio)
        self.pf.update(portfolio='fake_portfolio', date='2014/12/25')
        eq_(self.pf.portfolio, 'fake_portfolio')
        eq_(self.pf.date, '2014/12/25')
        self.assertIsNone(self.pf.perfs)
        self.pf.update(
            portfolio='new_portfolio', date='2014/12/27', perfs='fake_perfs')
        eq_(self.pf.portfolio, 'new_portfolio')
        eq_(self.pf.date, '2014/12/27')
        eq_(self.pf.perfs, 'fake_perfs')

    def test_overload_optimize(self):
        alloc, e_ret, e_risk = self.pf.optimize(
            date='2014/12/25',
            to_buy={'su.pa': 34.5},
            to_sell={'tec.pa': 45.4},
            parameters={}
        )
        eq_(e_ret, 0)
        eq_(e_risk, 1)
        eq_(alloc['date'], '2014/12/25')
        eq_(alloc['buy'], {'su.pa': 34.5})

    def test_trade_signals_handler(self):
        signals = {
            'buy': {'su.pa': 34.5},
            'sell': {'tec.pa': 45.4}
        }
        alloc = self.pf.trade_signals_handler(signals)
        self.assertIsNone(alloc['date'])
        eq_(alloc['buy'], signals['buy'])

    @raises(portfolio.PortfolioOptimizationFailed)
    def test_error_while_opitmizing(self):
        signals = {
            'buy': {'su.pa': 34.5},
            'sell': {'tec.pa': 45.4}
        }
        pf = test_utils.TestPortfolio({'raise_fake_error': True})
        pf.trade_signals_handler(signals)
