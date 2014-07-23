# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Benchmark loader modified to allow live data streaming (broken)
  ------------------------------------------------------

  :copyright (c) 2014 Xavier Bruhiere.
  :license: Apache2.0, see LICENSE for more details.
'''

import random
import pandas as pd
from datetime import datetime
from collections import OrderedDict
import zipline.data.loader as zipline
from zipline.utils.tradingcalendar import (
    trading_day,
    trading_days
)
import dna.logging

log = dna.logging.logger(__name__)


# TODO Would find a place in utils or dna project
def normalize_date(test_date):
    ''' Same function as zipline.finance.trading.py'''
    test_date = pd.Timestamp(test_date, tz='UTC')
    return pd.tseries.tools.normalize_date(test_date)


# TODO Add documentation
class FactoryBenchmark(object):
    ''' Base class for custom benchmark data loader '''

    def __init__(self, frequency='daily'):
        # Make data reproductible
        random.seed(frequency)
        if frequency == 'minutely':
            self.offset = pd.datetools.Minute()
        elif frequency == 'hourly':
            self.offset = pd.datetools.Hour()
        elif frequency == 'daily':
            self.offset = pd.datetools.Day()
        else:
            raise NotImplementedError(
                'Only minutely, hourly and daily frequencies are supported'
            )

    def _random_future_treasury(self, dates):
        log.info('Making up fake treasury market values')
        # NOTE What is tr_curves['tid'] ?
        # TODO Make the fake computation more efficient
        # Compute it once
        dates_length = len(dates)
        tr_fake = OrderedDict(sorted(
            ((pd.Timestamp(dates[0] + i * self.offset),
              {'date': date,
                'tid': i + dates_length,
                '30year': random.randrange(-0.1, 0.1, int=float),
                '20year': random.randrange(-0.1, 0.1, int=float),
                '10year': random.randrange(-0.1, 0.1, int=float),
                '7year': random.randrange(-0.1, 0.1, int=float),
                '5year': random.randrange(-0.1, 0.1, int=float),
                '3year': random.randrange(-0.1, 0.1, int=float),
                '2year': random.randrange(-0.1, 0.1, int=float),
                '1year': random.randrange(-0.1, 0.1, int=float),
                '6month': random.randrange(-0.1, 0.1, int=float),
                '3month': random.randrange(-0.1, 0.1, int=float),
                '1month': random.randrange(-0.1, 0.1, int=float)
               })
             for i, date in enumerate(dates)),
            key=lambda t: t[0]))

        return tr_fake

    def _random_future_benchmark(self, dates, bm_symbol):
        ''' Simulate futur values between reasonable '''
        log.info('Making up fake benchmark market values')
        # TODO Compute -0.16, 0.2 from past data
        return pd.Series(
            [random.randrange(-0.16, 0.2, int=float) for _ in dates],
            index=dates
        )


class LiveBenchmark(FactoryBenchmark):
    ''' extend zipline loader with future values '''

    def surcharge_market_data(self, bm_symbol='^GSPC'):
        log.info('Loading benchmark and treasury data')
        bm_bt, tr_bt = zipline.load_market_data(bm_symbol)

        event_dt = normalize_date(datetime.now())
        dates = pd.date_range(event_dt, periods=(len(bm_bt) / 2))
        bm_live = self._random_future_benchmark(dates, bm_symbol)
        tr_live = self._random_future_treasury(dates)

        bm = bm_bt.append(bm_live)
        tr_bt.update(tr_live)
        log.debug('Done ({} events)'.format(len(bm.index)))
        return bm, tr_bt


class OfflineBenchmark(FactoryBenchmark):
    ''' Follow the same logic as LiveBenchmark, but avoid data downloading
    part zipline uses with load_market_data '''

    _fake_start = '2008/07/08'
    _fake_end = '2016/01/01'

    def surcharge_market_data(self, bm_symbol='^GSPC'):
        '''
        Replace default zipline implementation for benchmark data loading
        '''
        most_recent = pd.Timestamp('today', tz='UTC') - trading_day
        most_recent_index = trading_days.searchsorted(most_recent)
        days_up_to_now = trading_days[:most_recent_index]
        dates = days_up_to_now + pd.date_range(
            normalize_date(most_recent), normalize_date(self._fake_end))

        tr_fake = self._random_future_treasury(dates)
        bm_fake = self._random_future_benchmark(dates, bm_symbol)

        log.debug('Done ({} events)'.format(len(bm_fake.index)))
        return bm_fake, tr_fake
