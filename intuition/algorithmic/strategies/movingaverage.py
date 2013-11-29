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


import pytz
import datetime
import numpy as np

from zipline.algorithm import TradingAlgorithm
from zipline.transforms import MovingAverage, MovingVWAP, batch_transform


class DualMovingAverage(TradingAlgorithm):
    """Dual Moving Average Crossover algorithm.
    This algorithm buys apple once its short moving average crosses
    its long moving average (indicating upwards momentum) and sells
    its shares once the averages cross again (indicating downwards
    momentum).
    """
    def initialize(self, properties):
        self.save = properties.get('save', False)
        long_window        = properties.get('long_window', 400)
        short_window       = properties.get('short_window', None)
        if short_window is None:
            short_window = int(round(properties.get('ma_rate', 0.5) * float(long_window), 2))
        self.threshold     = properties.get('threshold', 0)
        self.debug         = properties.get('debug', 0)

        self.add_transform(MovingAverage, 'short_mavg', ['price'],
                           window_length=short_window)

        self.add_transform(MovingAverage, 'long_mavg', ['price'],
                           window_length=long_window)

        # To keep track of whether we invested in the stock or not
        self.invested    = {}

        self.short_mavgs = []
        self.long_mavgs  = []

    def handle_data(self, data):
        ''' ----------------------------------------------------------    Init   --'''
        if self.initialized:
            instructions = self.manager.update(
                    self.portfolio,
                    self.datetime.to_pydatetime(),
                    self.perf_tracker.cumulative_risk_metrics.to_dict(),
                    save=self.save,
                    widgets=False)
            for t in data:
                self.invested[t] = False
        else:
            self.initialized = True
        signals = {}

        ''' ----------------------------------------------------------    Scan   --'''
        for ticker in data:
            short_mavg = data[ticker].short_mavg['price']
            long_mavg = data[ticker].long_mavg['price']
            if short_mavg - long_mavg > self.threshold and not self.invested[ticker]:
                signals[ticker] = data[ticker].price
                self.invested[ticker] = True
            elif short_mavg - long_mavg < -self.threshold and self.invested[ticker]:
                signals[ticker] = - data[ticker].price
                self.invested[ticker] = False

        ''' ----------------------------------------------------------   Orders  --'''
        if signals:
            orderBook = self.manager.trade_signals_handler(signals)
            for ticker in orderBook:
                if self.debug:
                    self.logger.notice('{} Ordering {} {} stocks'
                            .format(self.datetime, ticker, orderBook[ticker]))
                self.order(ticker, orderBook[ticker])

        # Save mavgs for later analysis.
        self.short_mavgs.append(short_mavg)
        self.long_mavgs.append(long_mavg)


class VolumeWeightAveragePrice(TradingAlgorithm):
    '''https://www.quantopian.com/posts/updated-multi-sid-example-algorithm-1'''
    def initialize(self, properties):
        # Common setup
        self.save    = properties.get('save', 0)
        self.debug   = properties.get('debug', 0)

        self.buy_trigger = properties.get('buy_trigger', 0.995)
        self.sell_trigger = properties.get('sell_trigger', 1.005)

        # Here we initialize each stock.  Note that we're not storing integers; by
        # calling sid(123) we're storing the Security object.
        self.vwap = {}
        self.price = {}

        # Setting our maximum position size, like previous example
        self.max_notional = 1000000.1
        self.min_notional = -1000000.0

        # initializing the time variables we use for logging
        self.d = datetime.datetime(2005, 1, 10, 0, 0, 0, tzinfo=pytz.utc)

        self.add_transform(MovingVWAP, 'vwap', market_aware=True,
                window_length=properties.get('window_length', 3))

    def handle_data(self, data):
        ''' ----------------------------------------------------------    Init   --'''
        if self.initialized:
            instruction = self.manager.update(
                    self.portfolio,
                    self.datetime.to_pydatetime(),
                    self.perf_tracker.cumulative_risk_metrics.to_dict(),
                    save=self.save,
                    widgets=False)
        else:
            self.initialized = True

        signals = {}

        # Initializing the position as zero at the start of each frame
        notional = 0

        ''' ----------------------------------------------------------    Scan   --'''
        # This runs through each stock.  It computes
        # our position at the start of each frame.
        for stock in data:
            price = data[stock].price
            notional = notional + self.portfolio.positions[stock].amount * price
            tradeday = data[stock].datetime

        # This runs through each stock again.  It finds the price and calculates
        # the volume-weighted average price.  If the price is moving quickly, and
        # we have not exceeded our position limits, it executes the order and
        # updates our position.
        for stock in data:
            vwap = data[stock].vwap
            price = data[stock].price

            if price < vwap * self.buy_trigger and notional > self.min_notional:
                signals[stock] = price
            elif price > vwap * self.sell_trigger and notional < self.max_notional:
                signals[stock] = - price

        # If this is the first trade of the day, it logs the notional.
        if (self.d + datetime.timedelta(days=1)) < tradeday:
            self.logger.debug(str(notional) + ' - notional start ' + tradeday.strftime('%m/%d/%y'))
            self.d = tradeday

        ''' ----------------------------------------------------------   Orders  --'''
        if signals and self.datetime.to_pydatetime() > self.portfolio.start_date:
            order_book = self.manager.trade_signals_handler(signals)
            for stock in order_book:
                if self.debug:
                    self.logger.notice('{}: Ordering {} {} stocks'.format(
                        self.datetime, stock, order_book[stock]))
                self.order(stock, order_book[stock])
                notional = notional + price * order_book[stock]


class Momentum(TradingAlgorithm):
    '''
    https://www.quantopian.com/posts/this-is-amazing
    !! Many transactions, so makes the algorithm explode when traded with many positions
    '''
    def initialize(self, properties):
        self.save    = properties.get('save', 0)
        self.debug   = properties.get('debug', 0)

        self.max_notional = 100000.1
        self.min_notional = -100000.0

        self.add_transform(MovingAverage, 'mavg', ['price'],
                window_length=properties.get('window_length', 3))

    def handle_data(self, data):
        ''' ----------------------------------------------------------    Init   --'''
        if self.initialized:
            instruction = self.manager.update(
                    self.portfolio,
                    self.datetime.to_pydatetime(),
                    self.perf_tracker.cumulative_risk_metrics.to_dict(),
                    save=self.save,
                    widgets=False)
        else:
            self.initialized = True
        signals = dict()
        notional = 0

        ''' ----------------------------------------------------------    Scan   --'''
        for ticker in data:
            sma          = data[ticker].mavg.price
            price        = data[ticker].price
            cash         = self.portfolio.cash
            notional     = self.portfolio.positions[ticker].amount * price
            capital_used = self.portfolio.capital_used

            # notional stuff are portfolio strategies, implement a new one, combinaison => parameters !
            if sma > price and notional > -0.2 * (capital_used + cash):
                signals[ticker] = price
            elif sma < price and notional < 0.2 * (capital_used + cash):
                signals[ticker] = - price
        
        ''' ----------------------------------------------------------   Orders  --'''
        if signals:
            order_book = self.manager.trade_signals_handler(signals)
            for ticker in order_book:
                self.order(ticker, order_book[ticker])
                if self.debug:
                    self.logger.notice('{}: Ordering {} {} stocks'.format(
                        self.datetime, ticker, order_book[ticker]))


class MovingAverageCrossover(TradingAlgorithm):
    '''
    https://www.quantopian.com/posts/moving-average-crossover
    '''
    def initialize(self, properties):
        self.debug = properties.get('debug', 0)
        self.save  = properties.get('save', 0)

        self.fast = []
        self.slow = []
        self.medium = []
        self.breakoutFilter = 0

        self.passedMediumLong = False
        self.passedMediumShort = False

        self.holdingLongPosition = False
        self.holdingShortPosition = False

        self.entryPrice = 0.0

    def handle_data(self, data):
        ''' ----------------------------------------------------------    Init   --'''
        if self.initialized:
            user_instruction = self.manager.update(
                    self.portfolio,
                    self.datetime.to_pydatetime(), 
                    self.perf_tracker.cumulative_risk_metrics.to_dict(),
                    save=self.save,
                    widgets=False)
        else:
            # Perf_tracker need at least a turn to have an index
            self.initialized = True

        signals = {}

        ''' ----------------------------------------------------------    Scan   --'''
        for ticker in data:
            self.fast.append(data[ticker].price)
            self.slow.append(data[ticker].price)
            self.medium.append(data[ticker].price)

            fastMovingAverage = 0.0
            mediumMovingAverage = 0.0
            slowMovingAverage = 0.0

            if len(self.fast) > 30:
                self.fast.pop(0)
                fastMovingAverage = sum(self.fast) / len(self.fast)

            if len(self.medium) > 60 * 30:
                self.medium.pop(0)
                mediumMovingAverage = sum(self.medium) / len(self.medium)

            if len(self.slow) > 60 * 60:
                self.slow.pop(0)
                slowMovingAverage = sum(self.slow) / len(self.slow)

            if ((self.holdingLongPosition is False and self.holdingShortPosition is False)
                    and ((mediumMovingAverage > 0.0 and slowMovingAverage > 0.0)
                    and (mediumMovingAverage > slowMovingAverage))):
                self.passedMediumLong = True

            if ((self.holdingLongPosition is False and self.holdingShortPosition is False)
                     and ((mediumMovingAverage > 0.0 and slowMovingAverage > 0.0)
                     and (mediumMovingAverage < slowMovingAverage))):
                self.passedMediumShort = True

            # Entry Strategies
            if (self.holdingLongPosition is False and self.holdingShortPosition is False
                     and self.passedMediumLong is True
                     and ((fastMovingAverage > 0.0 and slowMovingAverage > 0.0)
                     and (fastMovingAverage > mediumMovingAverage))):

                if self.breakoutFilter > 5:
                    self.logger.info("ENTERING LONG POSITION")
                    signals[ticker] = data[ticker].price

                    self.holdingLongPosition = True
                    self.breakoutFilter = 0
                    self.entryPrice = data[ticker].price
                else:
                    self.breakoutFilter += 1

            if (self.holdingShortPosition is False and self.holdingLongPosition is False
                    and self.passedMediumShort is True
                    and ((fastMovingAverage > 0.0 and slowMovingAverage > 0.0)
                    and (fastMovingAverage < mediumMovingAverage))):

                if self.breakoutFilter > 5:
                    self.logger.info("ENTERING SHORT POSITION")
                    #self.order(ticker, -100)
                    signals[ticker] = - data[ticker].price
                    self.holdingShortPosition = True
                    self.breakoutFilter = 0
                    self.entryPrice = data[ticker].price
                else:
                    self.breakoutFilter += 1

        # Exit Strategies
        if (self.holdingLongPosition is True
                    and ((fastMovingAverage > 0.0 and slowMovingAverage > 0.0)
                    and (fastMovingAverage < mediumMovingAverage))):

            if self.breakoutFilter > 5:
                signals[ticker] = - data[ticker].price
                self.holdingLongPosition = False
                self.breakoutFilter = 0
            else:
                self.breakoutFilter += 1

        if (self.holdingShortPosition is True
                and ((fastMovingAverage > 0.0 and slowMovingAverage > 0.0)
                and (fastMovingAverage > mediumMovingAverage))):
            if self.breakoutFilter > 5:
                signals[ticker] = data[ticker].price
                self.holdingShortPosition = False
                self.breakoutFilter = 0
            else:
                self.breakoutFilter += 1
        ''' ---------------------------------------------------   Orders  --'''
        self.process_signals(signals)

    def process_signals(self, signals):
        if not signals:
            return

        order_book = self.manager.trade_signals_handler(signals)

        for ticker in order_book:
            if self.debug:
                self.logger.notice('{} Ordering {} {} stocks'.format(
                    self.datetime, ticker, order_book[ticker]))
            self.order(ticker, order_book[ticker])
