'''
Tests for intuition.data.universe
'''

import os
import unittest
from nose.tools import raises, eq_
import intuition.test_utils as test_utils
import intuition.data.universe as universe
from intuition.errors import LoadMarketSchemeFailed


class MarketTestCase(unittest.TestCase):

    def setUp(self):
        test_utils.setup_logger(self)
        self.default_timezone = 'US/Eastern'
        self.default_benchmark = '^GSPC'
        self.scheme_path = os.path.expanduser('~/.intuition/data/market.yml')
        self.good_universe_description = 'stocks:paris:cac40'
        self.bad_universe_description = 'whatever'

    def tearDown(self):
        test_utils.teardown_logger(self)

    # NOTE It also tests market._load_market_scheme()
    def test_initialize_market(self):
        market = universe.Market()
        self.assertIsInstance(market.scheme, dict)
        eq_(market.benchmark, self.default_benchmark)
        eq_(market.timezone, self.default_timezone)
        #eq_(market.open, self.default_open)
        #eq_(market.close, self.default_close)

    def test_initialize_market_without_scheme(self):
        tmp_path = self.scheme_path.replace('market', 'bkp.market')
        os.system('mv {} {}'.format(self.scheme_path, tmp_path))
        self.assertRaises(LoadMarketSchemeFailed, universe.Market)
        os.system('mv {} {}'.format(tmp_path, self.scheme_path))

    def test__extract_forex(self):
        market = universe.Market()
        sids = market._extract_forex()
        self.assertGreater(len(sids), 0)
        self.assertGreater(sids[0].find('/'), 0)

    def test__extract_cac40(self):
        market = universe.Market()
        sids = market._extract_cac40(['stocks', 'paris', 'cac40'])
        self.assertGreater(len(sids), 0)
        self.assertGreater(sids[0].find('.pa'), 0)

    def test__lookup_sids_no_limit(self):
        market = universe.Market()
        sids = market._lookup_sids(self.good_universe_description)
        self.assertIsInstance(sids, list)
        self.assertGreater(len(sids), 0)

    def test__lookup_sids_with_limit(self):
        limit = 4
        market = universe.Market()
        sids = market._lookup_sids(self.good_universe_description, limit)
        self.assertIsInstance(sids, list)
        eq_(len(sids), limit)

    @raises(LoadMarketSchemeFailed)
    def test__lookup_sids_wrong_market(self):
        market = universe.Market()
        market._lookup_sids(self.bad_universe_description)

    def test_parse_universe(self):
        market = universe.Market()
        market.parse_universe_description(
            self.good_universe_description + ',4')
        self.assertIsInstance(market.sids, list)
        eq_(len(market.sids), 4)
