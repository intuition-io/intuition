# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Intuition test utilities
  ------------------------

  :copyright (c) 2014 Xavier Bruhiere
  :license: Apache 2.0, see LICENSE for more details.
'''

import pandas as pd
import pytz
from random import random
from intuition.data.universe import Market
from intuition.api.context import ContextFactory
from intuition.api.datafeed import HybridDataFactory
from intuition.api.portfolio import PortfolioFactory
from intuition.api.algorithm import TradingFactory


class FakeContext(ContextFactory):
    ''' Returns fake configuration '''

    def initialize(self, storage):
        self.storage = storage
        self.raise_error = not bool(storage['params'].get('valid', True))
        self.bad_format = bool(storage['params'].get('format', False))

    def load(self):
        if self.raise_error:
            raise ValueError
        return {
            'universe': 'forex,5',
            'index': pd.date_range('2012/01/01', '2012/02/01'),
            'modules': {
                'algorithm': 'fake_algorithm',
                'manager': 'fake_manager',
                'backtest': 'fake_backtest',
                'live': 'fake_live'
            }
        } if not self.bad_format else {}


class TestAlgorithm(TradingFactory):
    ''' Returns minimal algorithm for tests '''
    warmed_data = None

    def initialize(self, properties):
        self.properties = properties

    def warm(self, data):
        self.warmed_data = data

    def event(self, data):
        return {}


class TestPortfolio(PortfolioFactory):
    ''' Returns minimal portfolio for tests '''
    initialized = False

    def initialize(self, properties):
        self.initialized = True

    def optimize(self, to_buy, to_sell):
        if 'raise_fake_error' in self.properties:
            raise ValueError('whatever error')
        return {'date': self.date, 'buy': to_buy}, 0, 1


class FakeBacktestDatasource(object):

    def __init__(self, sids, properties):
        pass

    @property
    def mapping(self):
        return {
            'backtest': (lambda x: True, 'sid'),
            'dt': (lambda x: x, 'dt'),
            'sid': (lambda x: x, 'sid'),
            'price': (float, 'price'),
            'volume': (int, 'volume'),
        }

    def get_data(self, sids, start, end):
        index = pd.date_range(start, end, tz=pytz.utc)
        return pd.DataFrame({sid: [random()] * len(index)
                            for sid in sids}, index=index)


class FakePanelBacktestDatasource(object):

    def __init__(self, sids, properties):
        pass

    @property
    def mapping(self):
        return {
            'backtest': (lambda x: True, 'sid'),
            'dt': (lambda x: x, 'dt'),
            'sid': (lambda x: x, 'sid'),
            'price': (float, 'price'),
            'low': (float, 'low'),
            'high': (float, 'high'),
            'volume': (int, 'volume'),
        }

    def get_data(self, sids, start, end):
        index = pd.date_range(start, end, tz=pytz.utc)
        fake_data = {}
        for sid in sids:
            fake_data[sid] = pd.DataFrame(
                {field: [random()] * len(index)
                 for field in ['price', 'low', 'high', 'volume']}, index=index)
        return pd.Panel(fake_data)


class FakePanelWithoutVolumeBacktestDatasource(object):

    def __init__(self, sids, properties):
        pass

    def get_data(self, sids, start, end):
        index = pd.date_range(start, end, tz=pytz.utc)
        fake_data = {}
        for sid in sids:
            fake_data[sid] = pd.DataFrame(
                {field: [random()] * len(index)
                 for field in ['price', 'low', 'high']}, index=index)
        return pd.Panel(fake_data)


class FakeLiveDatasource(object):

    def __init__(self, sids, properties):
        pass

    @property
    def mapping(self):
        return {
            'live': True
        }

    def get_data(self, sids, start, end):
        return pd.DataFrame()


def build_fake_hybridDataFactory(start='2012/01/01',
                                 end='2012/01/07',
                                 universe='forex,3'):
    test_index = pd.date_range(start, end, tz=pytz.utc)
    market_ = Market()
    market_.parse_universe_description(universe)
    return HybridDataFactory(
        universe=market_,
        index=test_index,
        backtest=FakeBacktestDatasource
    )
