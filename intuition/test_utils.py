# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Intuition test utilities
  ------------------------

  :copyright (c) 2014 Xavier Bruhiere
  :license: Apache 2.0, see LICENSE for more details.
'''

from logbook import FileHandler
import pandas as pd
from intuition.api.context import ContextFactory
from intuition.api.portfolio import PortfolioFactory
from intuition.api.algorithm import TradingFactory


def setup_logger(test, path='/tmp/tests-intuition.log'):
    test.log_handler = FileHandler(path)
    test.log_handler.push_application()


def teardown_logger(test):
    test.log_handler.pop_application()
    test.log_handler.close()


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

    def optimize(self, date, to_buy, to_sell, parameters):
        if 'raise_fake_error' in parameters:
            raise ValueError('whatever error')
        return {'date': date, 'buy': to_buy}, 0, 1
