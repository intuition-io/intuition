'''
Tests for intuition.utils
'''

import unittest
import pytz
import pandas
from datetime import datetime
import intuition.utils as utils


class ConfigurationTestCase(unittest.TestCase):

    def test_is_live(self):
        last_trade_date = datetime(2026, 1, 1, tzinfo=pytz.utc)
        self.assertTrue(utils.is_live(last_trade_date))

    def test_is_not_live(self):
        last_trade_date = datetime(1789, 1, 1, tzinfo=pytz.utc)
        self.assertFalse(utils.is_live(last_trade_date))

    def test_normalize_epoch_date(self):
        epoch_date = 15334321432
        norm_date = utils.normalize_date_format(epoch_date)
        self.assertIsInstance(norm_date, datetime)
        self.assertEquals(norm_date.tzinfo, pytz.utc)

    def test_timezone_detection(self):
        timezone = utils._detect_timezone()
        self.assertIsInstance(timezone, str)
        details = timezone.split('/')
        self.assertEqual(len(details), 2)

    def test_normalize_human_date(self):
        human_date = '23h16'
        norm_date = utils.normalize_date_format(human_date)
        self.assertIsInstance(norm_date, datetime)
        self.assertEqual(norm_date.minute, 16)
        self.assertEquals(norm_date.tzinfo, pytz.utc)

    def _validate_dates_index(self, index):
        self.assertIsInstance(index, pandas.tseries.index.DatetimeIndex)
        self.assertGreater(len(index), 1)
        self.assertEqual(index.tzinfo, pytz.utc)

    def test_build_date_index(self):
        self._validate_dates_index(utils.build_date_index())
        self._validate_dates_index(utils.build_date_index(
            start=datetime(2011, 1, 1, tzinfo=pytz.utc)))
        self._validate_dates_index(utils.build_date_index(
            end=datetime(2014, 1, 1, tzinfo=pytz.utc)))
        self._validate_dates_index(utils.build_date_index(
            end=datetime(2014, 1, 1, tzinfo=pytz.utc), freq='M'))
        self._validate_dates_index(utils.build_date_index(
            start=datetime(2011, 1, 1, tzinfo=pytz.utc),
            end=datetime(2014, 1, 1, tzinfo=pytz.utc)))

    def test_utc_date_to_epoch(self):
        utc_date = datetime(2012, 12, 1, tzinfo=pytz.utc)
        epoch = utils.UTC_date_to_epoch(utc_date)
        self.assertIsInstance(epoch, int)
        self.assertGreater(epoch, 1000000000)

    def test_epoch_to_date(self):
        date = utils.epoch_to_date(1392934500)
        self.assertIsInstance(date, datetime)
        self.assertEquals(date.tzinfo, pytz.utc)

    def test_epoch_conversions(self):
        date = datetime(2012, 12, 1, tzinfo=pytz.utc)
        epoch = utils.UTC_date_to_epoch(date)
        new_date = utils.epoch_to_date(epoch)
        self.assertEqual(date, new_date)

    def test_wait_backtest_next_tick(self):
        old_dt = datetime(2010, 12, 1, tzinfo=pytz.utc)
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
