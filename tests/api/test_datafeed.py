'''
Tests for intuition.api.datafeed
'''

import unittest
from nose.tools import raises, ok_, eq_, nottest
from random import random
import pytz
import datetime as dt
import pandas as pd
import intuition.api.datafeed as datafeed
from intuition.data.universe import Market
from intuition.errors import InvalidDatafeed
from intuition.test_framework import (
    FakeLiveDatasource,
    FakeBacktestDatasource,
    FakePanelBacktestDatasource,
    FakePanelWithoutVolumeBacktestDatasource
)
import dna.test_utils


class DatafeedUtilsTestCase(unittest.TestCase):

    def setUp(self):
        dna.test_utils.setup_logger(self)
        self.fake_sid = 'fake_sid'
        self.fake_one_sid_series = pd.Series(
            {key: random() for key in ['low', 'close']})
        self.fake_multiple_sids_series = pd.Series(
            {key: random() for key in ['goog', 'fake_sid']})
        self.fake_multiple_sids_df = pd.DataFrame(
            {key: {'price': random(), 'close': 0.3}
             for key in ['goog', 'fake_sid']})
        self.fake_date = dt.datetime(2013, 1, 1)

    def tearDown(self):
        dna.test_utils.teardown_logger(self)

    @nottest
    def _check_event(self, event):
        self.assertIsInstance(event, dict)
        self.assertIn('volume', event)
        self.assertIn('dt', event)
        eq_(event['dt'], self.fake_date)
        eq_(event['sid'], self.fake_sid)

    def test_build_safe_event_without_volume(self):
        partial_event = self.fake_one_sid_series.to_dict()
        event = datafeed._build_safe_event(
            partial_event, self.fake_date, self.fake_sid)
        self._check_event(event)
        for field in self.fake_one_sid_series.index:
            self.assertIn(field, event.keys())

    def test_build_safe_event_with_volume(self):
        partial_event = self.fake_one_sid_series.to_dict()
        partial_event.update({'volume': 12034})
        event = datafeed._build_safe_event(
            partial_event, self.fake_date, self.fake_sid)
        self._check_event(event)
        for field in self.fake_one_sid_series.index:
            self.assertIn(field, event.keys())

    @raises(AttributeError)
    def test_wrong_data_type(self):
        wrong_type = bool
        datafeed._build_safe_event(wrong_type, self.fake_date, self.fake_sid)

    def test_check_data_modules(self):
        end = self.fake_date + pd.datetools.MonthBegin(6)
        ok_(datafeed._check_data_modules(
            'backtest.module', None, self.fake_date, end))

    @raises(InvalidDatafeed)
    def test_check_data_modules_all_nones(self):
        end = self.fake_date + pd.datetools.MonthBegin(6)
        datafeed._check_data_modules(None, None, self.fake_date, end)


class HybridDataFactoryTestCase(unittest.TestCase):

    def setUp(self):
        dna.test_utils.setup_logger(self)
        self.test_index = pd.date_range(
            '2012/01/01', '2012/01/7', tz=pytz.utc)
        self.test_universe = 'forex,5'
        self.market = Market()
        self.market.parse_universe_description(self.test_universe)
        self.test_sids = self.market.sids

    def tearDown(self):
        dna.test_utils.teardown_logger(self)

    @nottest
    def _check_datasource(self, source):
        ok_((source.index == self.test_index).all())
        eq_(source.start, self.test_index[0])
        eq_(source.end, self.test_index[-1])
        eq_(source.sids, self.test_sids)
        self.assertIsNone(source._raw_data)
        eq_(source.arg_string, source.instance_hash)
        eq_(source.event_type, 4)
        ok_(hasattr(source, 'log'))
        self.assertFalse(source._is_live)

    @raises(InvalidDatafeed)
    def test_data_source_without_modules(self):
        config = {
            'sids': self.test_sids,
            'index': self.test_index
        }
        datafeed.HybridDataFactory(**config)

    @raises(InvalidDatafeed)
    def test_data_source_invalid_index(self):
        config = {
            'sids': self.test_sids,
            'index': bool
        }
        datafeed.HybridDataFactory(**config)

    def test_minimal_data_source(self):
        source = datafeed.HybridDataFactory(
            universe=self.market,
            index=self.test_index,
            backtest=FakeBacktestDatasource)
        self._check_datasource(source)

    def test_hybrid_mapping(self):
        source = datafeed.HybridDataFactory(
            universe=self.market,
            index=self.test_index,
            backtest=FakeBacktestDatasource,
            live=FakeLiveDatasource)

        self.assertIn('backtest', source.mapping)
        source._is_live = True
        self.assertIn('live', source.mapping)


# TODO Test Live data sources
class SpecificMarketDataFactoryTestCase(unittest.TestCase):

    def setUp(self):
        dna.test_utils.setup_logger(self)
        self.test_index = pd.date_range(
            '2012/01/01', '2012/01/7', tz=pytz.utc)

    def tearDown(self):
        dna.test_utils.teardown_logger(self)

    def test_dataframe_forex_backtest_data_generation(self):
        test_universe = 'forex,5'
        market = Market()
        market.parse_universe_description(test_universe)
        source = datafeed.HybridDataFactory(
            universe=market,
            index=self.test_index,
            backtest=FakeBacktestDatasource)
        total_rows = 0
        for row in source.raw_data:
            if not total_rows:
                self.assertListEqual(
                    sorted(row.keys()),
                    sorted(['dt', 'price', 'sid', 'volume']))
            total_rows += 1
        eq_(total_rows, 2 * len(self.test_index) * len(market.sids))

    def test_dataframe_cac40_backtest_data_generation(self):
        test_universe = 'stocks:paris:cac40'
        market = Market()
        market.parse_universe_description(test_universe)
        source = datafeed.HybridDataFactory(
            universe=market,
            index=self.test_index,
            backtest=FakeBacktestDatasource)
        total_rows = 0
        for row in source.raw_data:
            if not total_rows:
                self.assertListEqual(
                    sorted(row.keys()),
                    sorted(['dt', 'price', 'sid', 'volume']))
            total_rows += 1
        eq_(total_rows, len(self.test_index) * len(market.sids))

    def test_panel_cac40_backtest_data_generation(self):
        test_universe = 'stocks:paris:cac40'
        market = Market()
        market.parse_universe_description(test_universe)
        source = datafeed.HybridDataFactory(
            universe=market,
            index=self.test_index,
            backtest=FakePanelBacktestDatasource)
        total_rows = 0
        for row in source.raw_data:
            if not total_rows:
                self.assertListEqual(
                    sorted(row.keys()),
                    sorted(['dt', 'price', 'low', 'high', 'sid', 'volume']))
            total_rows += 1
        eq_(total_rows, len(self.test_index) * len(market.sids))

    def test_panel_without_volume_cac40_backtest_data_generation(self):
        test_universe = 'stocks:paris:cac40,5'
        market = Market()
        market.parse_universe_description(test_universe)
        source = datafeed.HybridDataFactory(
            universe=market,
            index=self.test_index,
            backtest=FakePanelWithoutVolumeBacktestDatasource)
        total_rows = 0
        for row in source.raw_data:
            if not total_rows:
                self.assertListEqual(
                    sorted(row.keys()),
                    sorted(['dt', 'price', 'low', 'high', 'sid', 'volume']))
            total_rows += 1
        eq_(total_rows, len(self.test_index) * len(market.sids))
