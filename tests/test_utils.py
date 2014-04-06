'''
Tests for intuition.utils
'''

import unittest
import pytz
import datetime as dt
import pandas as pd
import intuition.utils as utils


class UtilsTestCase(unittest.TestCase):

    def test_is_live(self):
        last_trade_date = dt.datetime(2026, 1, 1, tzinfo=pytz.utc)
        self.assertTrue(utils.is_live(last_trade_date))

    def test_is_not_live(self):
        last_trade_date = dt.datetime(1789, 1, 1, tzinfo=pytz.utc)
        self.assertFalse(utils.is_live(last_trade_date))

    def test_normalize_epoch_date(self):
        epoch_date = 15334321432
        norm_date = utils.normalize_date_format(epoch_date)
        self.assertIsInstance(norm_date, dt.datetime)
        self.assertEquals(norm_date.tzinfo, pytz.utc)

    def test_timezone_detection(self):
        timezone = utils._detect_timezone()
        self.assertIsInstance(timezone, str)
        details = timezone.split('/')
        self.assertEqual(len(details), 2)

    def test_normalize_human_date(self):
        human_date = '23h16'
        norm_date = utils.normalize_date_format(human_date)
        self.assertIsInstance(norm_date, dt.datetime)
        self.assertEqual(norm_date.minute, 16)
        self.assertEquals(norm_date.tzinfo, pytz.utc)

    def test_normalize_naive_date(self):
        naive_date = dt.datetime.now()
        norm_date = utils.normalize_date_format(naive_date)
        self.assertIsInstance(norm_date, dt.datetime)
        self.assertEquals(norm_date.tzinfo, pytz.utc)

    def test_utc_date_to_epoch(self):
        utc_date = dt.datetime(2012, 12, 1, tzinfo=pytz.utc)
        epoch = utils.UTC_date_to_epoch(utc_date)
        self.assertIsInstance(epoch, int)
        self.assertGreater(epoch, 1000000000)

    def test_epoch_to_date(self):
        date = utils.epoch_to_date(1392934500)
        self.assertIsInstance(date, dt.datetime)
        self.assertEquals(date.tzinfo, pytz.utc)

    def test_epoch_conversions(self):
        date = dt.datetime(2012, 12, 1, tzinfo=pytz.utc)
        epoch = utils.UTC_date_to_epoch(date)
        new_date = utils.epoch_to_date(epoch)
        self.assertEqual(date, new_date)

    def test_wait_backtest_next_tick(self):
        old_dt = dt.datetime(2010, 12, 1, tzinfo=pytz.utc)
        self.assertFalse(utils.next_tick(old_dt))

    def test_wait_live_next_tick(self):
        pass

    def test_import_intuition_module(self):
        pass

    def test_import_bad_intuition_module(self):
        pass

    def test_truncate_float(self):
        original_float = 3.232999
        truncated_float = utils.truncate(original_float, n=2)
        self.assertIsInstance(truncated_float, float)
        self.assertGreater(original_float, truncated_float)

    def test_truncate_str(self):
        self.assertEqual(utils.truncate('nofloat'), 'nofloat')


class TradingTimelineTestCase(unittest.TestCase):

    def _validate_dates(self, dates):
        self.assertIsInstance(dates, pd.tseries.index.DatetimeIndex)
        self.assertGreater(len(dates), 1)
        self.assertEqual(dates.tzinfo, pytz.utc)

    def test__build_backtest_trading_timeline(self):
        for start in ['2012/01/01', None]:
            for end in ['2013/01/01', None]:
                if not start and not end:
                    # This is live trading on one day
                    continue
                dates = utils.build_trading_timeline(start, end)
                self._validate_dates(dates)
                self.assertEqual(pd.tseries.offsets.Day(1), dates.freq)
                self.assertEqual(dates[0].hour, 23)

    def test__build_live_trading_timeline(self):
        freq = '3min'
        now = dt.datetime.now(pytz.utc)
        for start in [None, now + pd.tseries.offsets.Minute(5)]:
            for end in [None, '2014/06/01']:
                dates = utils.build_trading_timeline(start, end, freq=freq)
                self._validate_dates(dates)
                self.assertEqual(pd.tseries.offsets.Minute(3), dates.freq)
                self.assertGreater(dates[1], now)
                self.assertGreater(dates[-1], now)

    def test__build_hybrid_trading_timeline(self):
        freq = '3min'
        now = dt.datetime.now(pytz.utc)
        start = '2014/01/01'
        end = '2014/06/01'
        dates = utils.build_trading_timeline(start, end, freq)
        self._validate_dates(dates)
        self.assertEqual(dt.timedelta(0, 180), dates[-1] - dates[-2])
        self.assertGreater(now, dates[1])
        self.assertGreater(dates[-1], now)
