'''
Tests for intuition.api.algorithm
'''

import unittest
from nose.tools import raises, ok_, eq_, nottest
import intuition.test_utils as test_utils
import pandas as pd
import pytz
import datetime as dt
from intuition.api.datafeed import HybridDataFactory
from intuition.data.universe import Market
from test_datafeed import FakeBacktestDatasource


# TODO Test with a manager
class AlgorithmTestCase(unittest.TestCase):

    def setUp(self):
        test_utils.setup_logger(self)
        self.test_index = pd.date_range(
            '2012/01/01', '2012/01/7',
            tz=pytz.utc)
        self.today = dt.datetime.today()
        self.past_date = self.today - dt.timedelta(days=10)
        self.test_properties = {'test': True}
        self.algo = test_utils.TestAlgorithm(properties=self.test_properties)

    def tearDown(self):
        test_utils.teardown_logger(self)

    @nottest
    def _setup_source(self):
        market = Market()
        market.parse_universe_description('forex,5')
        return HybridDataFactory(
            universe=market,
            index=self.test_index,
            backtest=FakeBacktestDatasource)

    @nottest
    def _check_algorithm_object(self, algo):
        eq_(algo.days, 0)
        self.assertFalse(algo.auto)
        self.assertFalse(algo.initialized)
        self.assertIsNone(algo.realworld)
        self.assertIsNone(algo.sim_params)
        eq_(algo.sids, [])
        eq_(algo.middlewares, [])
        eq_(algo.sources, [])
        eq_(algo.capital_base, 100000.0)

    def test_new_algorithm(self):
        self.assertIsNone(self.algo.manager)
        self._check_algorithm_object(self.algo)

    @raises(TypeError)
    def test_new_algorithm_without_properties(self):
        test_utils.TestAlgorithm()

    def test_overload_initialize(self):
        eq_(self.algo.properties, self.test_properties)

    def test__is_interactive(self):
        self.algo.realworld = False
        for self.algo.datetime in [self.past_date, self.today]:
            ok_(self.algo._is_interactive())
        self.algo.realworld = True
        self.algo.datetime = self.today
        ok_(self.algo._is_interactive())
        self.algo.datetime = self.past_date
        self.assertFalse(self.algo._is_interactive())

    def test_run_algorithm(self):
        results = self.algo.run(self._setup_source())
        ok_(not results.empty)

    def test_warm_overload(self):
        pass
