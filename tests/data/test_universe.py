'''
Tests for intuition.data.universe
'''

import os
import unittest
from nose.tools import raises, eq_
import pytz
import pandas as pd
import datetime as dt
import dna.test_utils
import intuition.data.universe as universe
from intuition.errors import LoadMarketSchemeFailed


# TODO Test parse, parse_punctual, parse_constant_frequency
class TickTestCase(unittest.TestCase):

    def setUp(self):
        self.default_tz = 'UTC'
        self.default_delta = dt.timedelta(hours=1)
        self.default_start = pd.datetools.normalize_date(
            dt.datetime.now(tz=pytz.utc))
        self.default_end = pd.datetools.normalize_date(
            self.default_start + dt.timedelta(days=1))

    def test_default_new_tick(self):
        tick_ = universe.Tick()
        eq_(tick_.delta, self.default_delta)
        eq_(tick_.start, self.default_start)
        eq_(tick_.end, self.default_end)
        eq_(tick_._tz, self.default_tz)

    def test_tack_generator(self):
        tick_ = universe.Tick()
        dates = [date for date in tick_.tack]
        eq_(dates, filter(lambda x: isinstance(x, dt.datetime), dates))
        eq_(dates, filter(lambda x: x.tzinfo == pytz.utc, dates))
        eq_(dates[0], tick_.start)
        self.assertLessEqual(dates[-1], tick_.end)

    def test_trick_new_tick_params(self):
        now = dt.datetime.now(tz=pytz.utc)
        custom_start = now - dt.timedelta(hours=5)
        custom_end = now + dt.timedelta(hours=5)
        tick_ = universe.Tick(
            start=custom_start,
            end=custom_end,
            delta=dt.timedelta(minutes=33),
            tz='Europe/Paris'
        )
        eq_(tick_.delta, dt.timedelta(minutes=33))
        eq_(tick_.start, custom_start)
        eq_(tick_.end, custom_end)
        eq_(tick_._tz, 'Europe/Paris')

        dates = [date for date in tick_.tack]
        eq_(dates, filter(lambda x: isinstance(x, dt.datetime), dates))
        eq_(dates, filter(lambda x: x.tzinfo == pytz.utc, dates))
        eq_(dates[0], tick_.start)
        self.assertLessEqual(dates[-1], tick_.end)


class MarketTestCase(unittest.TestCase):

    def setUp(self):
        dna.test_utils.setup_logger(self)
        self.default_timezone = 'US/Eastern'
        self.default_benchmark = '^GSPC'
        self.scheme_path = os.path.expanduser('~/.intuition/data/market.yml')
        self.good_universe_description = 'stocks:paris:cac40'
        self.bad_universe_description = 'whatever'

    def tearDown(self):
        dna.test_utils.teardown_logger(self)

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
