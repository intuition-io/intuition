#
# Copyright 2012 Xavier Bruhiere
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


'''
Tests for zipline style trading algorithmic class
'''

import unittest
from neuronquant.utils.test_utils import (
        setup_logger,
        teardown_logger
)
from datetime import datetime
import pytz


from neuronquant.gears import engine
from zipline.algorithm import TradingAlgorithm
from zipline.transforms import MovingAverage


class Test(TradingAlgorithm):
    '''
    https://www.quantopian.com/posts/this-is-amazing
    !! Many transactions, so makes the algorithm explode when traded with many positions
    '''
    def initialize(self, properties):
        self.debug = properties.get('debug', 0)
        window_length = properties.get('window_length', 3)
        self.purchase_price = 0
        self.orderCounter = 0
        self.amount = 10000
        self.add_transform(MovingAverage, 'mavg', ['price'], window_length=window_length)
        #self.add_transform(SMA, 'mavg', ['price'], window_length=window_length)
        self.totalProfit = 0
        self.max_notional = 100000.1
        self.min_notional = -100000.0

    def handle_data(self, data):
        ''' ----------------------------------------------------------    Scan   --'''
        for ticker in data:
            #sma          = data[ticker].mavg
            sma          = data[ticker].mavg.price
            price        = data[ticker].price
            cash         = self.portfolio.cash
            notional     = self.portfolio.positions[ticker].amount * price
            capital_used = self.portfolio.capital_used

            if sma * 0.95 > price :
                self.logger.info('Cash : {} Notional : {} Capital used {} ' , cash , notional , capital_used)
                self.order(ticker, self.amount)
                self.logger.info('Cash : {} Notional : {} Capital used {} ' , cash , notional , capital_used)
                self.purchase_price += price
                self.orderCounter += 1
                if self.debug:
                    self.logger.info('{}: Ordering {} {} stocks @ {} '.format(self.datetime, ticker, self.amount , self.purchase_price / self.orderCounter))
            elif self.orderCounter > 0 and self.purchase_price / self.orderCounter < 1.1 * price:
                self.logger.info('-Cash : {} Notional : {} Capital used {} ' , cash , notional , capital_used)
                self.order(ticker, -self.orderCounter * self.amount)
                self.logger.info('-Cash : {} Notional : {} Capital used {} ' , cash , notional , capital_used)
                self.totalProfit += (price - self.purchase_price / self.orderCounter) * self.amount * self.orderCounter
                if self.debug:
                    self.logger.info('{}: Selling {} {} stocks @ {} Profit : {}'.format(self.datetime, ticker, -self.orderCounter * self.amount, price , self.totalProfit))
                self.purchase_price = 0
                self.orderCounter = 0


class TestUserAlgo(unittest.TestCase):
    def setUp(self):
        setup_logger(self)
        self.configuration = {'algorithm': Test,
                'frequency': 'daily',
                'manager': '',
                'database': 'test',
                'tickers': ['goog', 'aapl'],
                'start': datetime(2008, 02, 02, tzinfo=pytz.utc),
                'end': datetime(2010, 01, 10, tzinfo=pytz.utc),
                'live': False,
                'port': 5555,
                'exchange': 'nasdaq',
                'cash': 100000,
                'remote': False
        }
        self.strategie = {'manager': {},
                'algorithm': {'debug': 1, 'window_length': 3}}

    def tearDown(self):
        teardown_logger(self)

    def test_avinashpandit_issue(self):
        '''
        Portfolio calculation issue
        '''
        core = engine.Simulation()
        data, trading_ctx = core.configure(self.configuration)
        analyzes = core.run(data, self.configuration, self.strategie, trading_ctx)
        assert analyzes
