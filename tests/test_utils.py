'''
Tests for intuition.utils
'''

import unittest
from nose.tools import ok_, eq_, nottest
import pytz
import datetime as dt
import pandas as pd
import intuition.utils as utils


class UtilsTestCase(unittest.TestCase):

    def test_is_live(self):
        last_trade_date = dt.datetime(2026, 1, 1, tzinfo=pytz.utc)
        ok_(utils.is_live(last_trade_date))

    def test_is_not_live(self):
        last_trade_date = dt.datetime(1789, 1, 1, tzinfo=pytz.utc)
        self.assertFalse(utils.is_live(last_trade_date))

    def test_wait_backtest_next_tick(self):
        old_dt = dt.datetime(2010, 12, 1, tzinfo=pytz.utc)
        self.assertFalse(utils.next_tick(old_dt))

    def test_wait_live_next_tick(self):
        pass

    def test_import_intuition_module(self):
        pass

    def test_import_bad_intuition_module(self):
        pass


class TradingTimelineTestCase(unittest.TestCase):

    @nottest
    def _validate_dates(self, dates):
        self.assertIsInstance(dates, pd.tseries.index.DatetimeIndex)
        self.assertGreater(len(dates), 0)
        eq_(dates.tzinfo, pytz.utc)

    def test__build_backtest_trading_timeline(self):
        for start in ['2012/01/01', None]:
            for end in ['2013/01/01', None]:
                if not start and not end:
                    # This is live trading on one day
                    continue
                dates = utils.build_trading_timeline(start, end)
                self._validate_dates(dates)
                eq_(pd.tseries.offsets.Day(1), dates.freq)

    def test__build_live_trading_timeline(self):
        now = dt.datetime.now(pytz.utc)
        for start in [None, now + pd.tseries.offsets.Minute(5)]:
            for end in [None, '2014/06/01']:
                dates = utils.build_trading_timeline(start, end)
                self._validate_dates(dates)
                self.assertGreater(dates[0], now)
                self.assertGreater(dates[-1], now)

    def test__build_hybrid_trading_timeline(self):
        now = dt.datetime.now(pytz.utc)
        start = '2014/01/01'
        end = '2014/06/01'
        dates = utils.build_trading_timeline(start, end)
        self._validate_dates(dates)
        # FIXME Almost a day
        #eq_(dt.timedelta(days=1), dates[-1] - dates[-2])
        self.assertGreater(now, dates[0])
        self.assertGreater(dates[-1], now)
