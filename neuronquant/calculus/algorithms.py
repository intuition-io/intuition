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


import datetime
import pytz
import numpy as np
import sys
import os

sys.path.append(os.environ['ZIPLINE'])
from zipline.algorithm import TradingAlgorithm
from zipline.transforms import MovingAverage, MovingVWAP, batch_transform, MovingStandardDev

import statsmodels.api as sm

from logbook import Logger


#TODO Override initialiez function with portfolio, logger and parameters initialization
#TODO Should handle in parameter all of the set_*
class BuyAndHold(TradingAlgorithm):
    '''Simpliest algorithm ever, just buy a stock at the first frame'''
    def initialize(self, properties):
        #NOTE You can't use it here, no self.manager yet. Issue ? Could configure every common parameters in Backtester engine
        #     and use setupe_strategie as an update
        #self.manager.setup_strategie({'commission_cost': self.commission.cost})
        pass

    def handle_data(self, data):
        #NOTE as self.frame_count, manager could be update in zipline.gens.tradesimulation, or use decorator ?
        ''' ----------------------------------------------------------    Init   --'''
        self.manager.update(self.portfolio, self.datetime.to_pydatetime())
        signals = dict()

        ''' ----------------------------------------------------------    Scan   --'''
        if self.frame_count == 3:
            for ticker in data:
                signals[ticker] = data[ticker].price

        ''' ----------------------------------------------------------   Orders  --'''
        if signals:
            orderBook = self.manager.trade_signals_handler(signals)
            for stock in orderBook:
                self.logger.info('{}: Ordering {} {} stocks'.format(self.datetime, stock, orderBook[stock]))
                self.order(stock, orderBook[stock])


class DualMovingAverage(TradingAlgorithm):
    """Dual Moving Average Crossover algorithm.
    This algorithm buys apple once its short moving average crosses
    its long moving average (indicating upwards momentum) and sells
    its shares once the averages cross again (indicating downwards
    momentum).
    """
    def initialize(self, properties):
        long_window        = properties.get('long_window', 400)
        short_window       = properties.get('short_window', None)
        if short_window is None:
            short_window = int(round(properties.get('ma_rate', 0.5) * float(long_window), 2))
        self.amount        = properties.get('amount', 10000)
        self.threshold     = properties.get('threshold', 0)
        #self.capital_base = properties.get('capital_base', 1000)
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
        self.manager.update(self.portfolio, self.datetime.to_pydatetime())
        signals = dict()
        #FIXME 2 is the first frame...
        #if (self.frame_count == 3):
        if self.init:
            self.init = False
            for t in data:
                self.invested[t] = False

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
                    self.logger.info('Ordering {} {} stocks'.format(ticker, orderBook[ticker]))
                self.order(ticker, orderBook[ticker])

        # Save mavgs for later analysis.
        self.short_mavgs.append(short_mavg)
        self.long_mavgs.append(long_mavg)


class VolumeWeightAveragePrice(TradingAlgorithm):
    '''https://www.quantopian.com/posts/updated-multi-sid-example-algorithm-1'''
    def initialize(self, properties):
        # Common setup
        self.debug    = properties.get('debug', 0)

        # Here we initialize each stock.  Note that we're not storing integers; by
        # calling sid(123) we're storing the Security object.
        self.vwap = {}
        self.price = {}

        # Setting our maximum position size, like previous example
        self.max_notional = 1000000.1
        self.min_notional = -1000000.0

        # initializing the time variables we use for logging
        self.d = datetime.datetime(2005, 1, 10, 0, 0, 0, tzinfo=pytz.utc)

        self.add_transform(MovingVWAP, 'vwap', market_aware=True, window_length=properties.get('window_length', 3))

    def handle_data(self, data):
        ''' ----------------------------------------------------------    Init   --'''
        signals = dict()
        self.manager.update(self.portfolio, self.datetime.to_pydatetime())

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

            if price < vwap * 0.995 and notional > self.min_notional:
                signals[stock] = price
            elif price > vwap * 1.005 and notional < self.max_notional:
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
                    self.logger.info('{}: Ordering {} {} stocks'.format(self.datetime, stock, order_book[stock]))
                self.order(stock, order_book[stock])
                notional = notional + price * order_book[stock]


class Momentum(TradingAlgorithm):
    '''
    https://www.quantopian.com/posts/this-is-amazing
    !! Many transactions, so makes the algorithm explode when traded with many positions
    '''
    def initialize(self, properties):
        self.debug    = properties.get('debug', 0)
        window_length = properties.get('window_length', 3)

        self.max_notional = 100000.1
        self.min_notional = -100000.0

        self.add_transform(MovingAverage, 'mavg', ['price'], window_length=window_length)

    def handle_data(self, data):
        ''' ----------------------------------------------------------    Init   --'''
        self.manager.update(self.portfolio, self.datetime.to_pydatetime())
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
                signals[ticker] = - price
            elif sma < price and notional < 0.2 * (capital_used + cash):
                signals[ticker] = price

        ''' ----------------------------------------------------------   Orders  --'''
        if signals:
            order_book = self.manager.trade_signals_handler(signals)
            for ticker in order_book:
                self.order(ticker, order_book[ticker])
                if self.debug:
                    self.logger.info('{}: Ordering {} {} stocks'.format(self.datetime, ticker, order_book[ticker]))
                    #self.logger.info('{}:  {} / {}'.format(self.datetime, sma, price))


class MovingAverageCrossover(TradingAlgorithm):
    '''
    https://www.quantopian.com/posts/moving-average-crossover
    '''
    def initialize(self, properties, strategie, parameters):
        self.debug    = properties.get('debug', 0)
        #window_length = properties.get('window_length', 3)
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
        self.manager.update(self.portfolio, self.datetime.to_pydatetime())
        #signals = dict()

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
                    self.order(ticker, 100)

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
                    self.order(ticker, -100)
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
                self.order(ticker, -100)
                self.holdingLongPosition = False
                self.breakoutFilter = 0
            else:
                self.breakoutFilter += 1

        if (self.holdingShortPosition is True
                and ((fastMovingAverage > 0.0 and slowMovingAverage > 0.0)
                and (fastMovingAverage > mediumMovingAverage))):
            if self.breakoutFilter > 5:
                self.order(ticker, 100)
                self.holdingShortPosition = False
                self.breakoutFilter = 0
            else:
                self.breakoutFilter += 1
        ''' ----------------------------------------------------------   Orders  --'''


class OLMAR(TradingAlgorithm):
    """
    On-Line Portfolio Moving Average Reversion

    More info can be found in the corresponding paper:
    http://icml.cc/2012/papers/168.pdf
    """
    def initialize(self, eps=1, window_length=5):
        #self.stocks = STOCKS
        #self.m = len(self.stocks)
        self.price = {}
        self.b_t = np.ones(self.m) / self.m
        self.last_desired_port = np.ones(self.m) / self.m
        self.eps = eps
        self.init = True
        self.days = 0
        self.window_length = window_length
        self.add_transform(MovingAverage, 'mavg', ['price'],
                           window_length=window_length)

        no_delay = datetime.timedelta(minutes=0)
        slip = self.slippage.VolumeShareSlippage(volume_limit=0.25,
                                            price_impact=0,
                                            delay=no_delay)
        self.set_slippage(slip)
        self.set_commission(self.commission.PerShare(cost=0))

    def handle_data(self, data):
        self.days += 1
        if self.days < self.window_length:
            return

        if self.init:
            self.rebalance_portfolio(data, self.b_t)
            self.init = False
            return

        m = self.m

        x_tilde = np.zeros(m)
        b = np.zeros(m)

        # find relative moving average price for each security
        for i, stock in enumerate(self.stocks):
            price = data[stock].price
            # Relative mean deviation
            x_tilde[i] = data[stock]['mavg']['price'] / price

        ###########################
        # Inside of OLMAR (algo 2)
        x_bar = x_tilde.mean()

        # market relative deviation
        mark_rel_dev = x_tilde - x_bar

        # Expected return with current portfolio
        exp_return = np.dot(self.b_t, x_tilde)
        weight = self.eps - exp_return
        variability = (np.linalg.norm(mark_rel_dev)) ** 2

        # test for divide-by-zero case
        if variability == 0.0:
            step_size = 0
        else:
            step_size = max(0, weight / variability)

        b = self.b_t + step_size * mark_rel_dev
        b_norm = simplex_projection(b)
        np.testing.assert_almost_equal(b_norm.sum(), 1)

        self.rebalance_portfolio(data, b_norm)

        # update portfolio
        self.b_t = b_norm

    def rebalance_portfolio(self, data, desired_port):
        #rebalance portfolio
        desired_amount = np.zeros_like(desired_port)
        current_amount = np.zeros_like(desired_port)
        prices = np.zeros_like(desired_port)

        if self.init:
            positions_value = self.portfolio.starting_cash
        else:
            positions_value = self.portfolio.positions_value + \
                self.portfolio.cash

        for i, stock in enumerate(self.stocks):
            current_amount[i] = self.portfolio.positions[stock].amount
            prices[i] = data[stock].price

        desired_amount = np.round(desired_port * positions_value / prices)

        self.last_desired_port = desired_port
        diff_amount = desired_amount - current_amount

        for i, stock in enumerate(self.stocks):
            self.order(stock, diff_amount[i])


def simplex_projection(v, b=1):
    """Projection vectors to the simplex domain

    Implemented according to the paper: Efficient projections onto the
    l1-ball for learning in high dimensions, John Duchi, et al. ICML 2008.
    Implementation Time: 2011 June 17 by Bin@libin AT pmail.ntu.edu.sg
    Optimization Problem: min_{w}\| w - v \|_{2}^{2}
    s.t. sum_{i=1}^{m}=z, w_{i}\geq 0

    Input: A vector v \in R^{m}, and a scalar z > 0 (default=1)
    Output: Projection vector w

    :Example:
    >>> proj = simplex_projection([.4 ,.3, -.4, .5])
    >>> print proj
    array([ 0.33333333, 0.23333333, 0. , 0.43333333])
    >>> print proj.sum()
    1.0

    Original matlab implementation: John Duchi (jduchi@cs.berkeley.edu)
    Python-port: Copyright 2012 by Thomas Wiecki (thomas.wiecki@gmail.com).
    """

    v = np.asarray(v)
    p = len(v)

    # Sort v into u in descending order
    v = (v > 0) * v
    u = np.sort(v)[::-1]
    sv = np.cumsum(u)

    rho = np.where(u > (sv - b) / np.arange(1, p + 1))[0][-1]
    theta = np.max([0, (sv[rho] - b) / (rho + 1)])
    w = (v - theta)
    w[w < 0] = 0
    return w


class StddevBased(TradingAlgorithm):
    def initialize(self, properties):
        self.debug    = properties.get('debug', 0)
        # Variable to hold opening price of long trades
        self.long_open_price = 0

        # Variable to hold stoploss price of long trades
        self.long_stoploss = 0

        # Variable to hold takeprofit price of long trades
        self.long_takeprofit = 0

        # Allow only 1 long position to be open at a time
        self.long_open = False

        # Initiate Tally of successes and fails

        # Initialised at 0.0000000001 to avoid dividing by 0 in winning_percentage calculation
        # (meaning that reporting will get more accurate as more trades are made, but may start
        # off looking strange)
        self.successes = 0.0000000001
        self.fails = 0.0000000001

        # Variable for emergency plug pulling (if you lose more than 30% starting capital,
        # trading ability will be turned off... tut tut tut :shakes head dissapprovingly:)
        self.plug_pulled = False

        self.add_transform(MovingStandardDev, 'stddev', window_length=properties.get('stddev', 9))
        self.add_transform(MovingVWAP, 'vwap', window_length=properties.get('vwap_window', 5))

    def handle_data(self, data):
        ''' ----------------------------------------------------------    Init   --'''
        # Reporting Variables
        profit = 0
        total_trades = self.successes + self.fails
        winning_percentage = self.successes / total_trades * 100

        ''' ----------------------------------------------------------    Scan   --'''
        # Data Variables
        for i, stock in enumerate(data.keys()):
            price = data[stock].price
            vwap_5_day = data[stock].vwap
            equity = self.portfolio.cash + self.portfolio.positions_value
            standard_deviation = data[stock].stddev
            if not standard_deviation:
                continue

            # Set order size

            # (Set here as "starting_cash/1000" - which coupled with the below
            # "and price < 1000" - is a scalable way of setting (initially :P)
            # affordable order quantities (for most stocks).

            order_amount = self.portfolio.starting_cash / 1000

            # Open Long Position if current price is larger than the 9 day volume weighted average
            # plus 60% of the standard deviation (meaning the price has broken it's range to the
            # up-side by 10% more than the range value)
            if price > vwap_5_day + (standard_deviation * 0.6) and self.long_open is False and price < 1000:
                self.order(stock, +order_amount)
                self.long_open = True
                self.long_open_price = price
                self.long_stoploss = self.long_open_price - standard_deviation * 0.6
                self.long_takeprofit = self.long_open_price + standard_deviation * 0.5
                self.logger.info('{}: Long Position Ordered'.format(self.datetime))

            # Close Long Position if takeprofit value hit

            # Note that less volatile stocks can end up hitting takeprofit at a small loss
            if price >= self.long_takeprofit and self.long_open is True:
                self.order(stock, -order_amount)
                self.long_open = False
                self.long_takeprofit = 0
                profit = (price * order_amount) - (self.long_open_price * order_amount)
                self.successes = self.successes + 1
                self.logger.info('Long Position Closed by Takeprofit at ${} profit'.format(profit))
                self.logger.info('Total Equity now at ${}'.format(equity))
                self.logger.info('So far you have had {} successful trades and {} failed trades'.format(self.successes, self.fails))
                self.logger.info('That leaves you with a winning percentage of {} percent'.format(winning_percentage))

            # Close Long Position if stoploss value hit
            if price <= self.long_stoploss and self.long_open is True:
                self.order(stock, -order_amount)
                self.long_open = False
                self.long_stoploss = 0
                profit = (price * order_amount) - (self.long_open_price * order_amount)
                self.fails = self.fails + 1
                self.logger.info('Long Position Closed by Stoploss at ${} profit'.format(profit))
                self.logger.info('Total Equity now at ${}'.format(equity))
                self.logger.info('So far you have had {} successful trades and {} failed trades'.format(self.successes, self.fails))
                self.logger.info('That leaves you with a winning percentage of {} percent'.format(winning_percentage))

            # Pull Plug?
            if equity < self.portfolio.starting_cash * 0.7:
                self.plug_pulled = True
                self.logger.info("Ouch! We've pulled the plug...")

            if self.plug_pulled is True and self.long_open is True:
                self.order(stock, -order_amount)
                self.long_open = False
                self.long_stoploss = 0
        ''' ----------------------------------------------------------   Orders  --'''


class Pairtrade(TradingAlgorithm):
    """Pairtrading relies on cointegration of two stocks.

    The expectation is that once the two stocks drifted apart
    (i.e. there is spread), they will eventually revert again. Thus,
    if we short the upward drifting stock and long the downward
    drifting stock (in short, we buy the spread) once the spread
    widened we can sell the spread with profit once they converged
    again. A nice property of this algorithm is that we enter the
    market in a neutral position.

    This specific algorithm tries to exploit the cointegration of
    Pepsi and Coca Cola by estimating the correlation between the
    two. Divergence of the spread is evaluated by z-scoring.
    """

    def initialize(self, window_length=100):
        self.spreads = []
        self.zscores = []
        self.invested = 0
        self.window_length = window_length
        self.ols_transform = ols_transform(refresh_period=self.window_length,
                                           window_length=self.window_length)

    def handle_data(self, data):
        ######################################################
        # 1. Compute regression coefficients between PEP and KO
        params = self.ols_transform.handle_data(data, 'PEP', 'KO')
        if params is None:
            return
        slope, intercept = params

        ######################################################
        # 2. Compute spread and zscore
        zscore = self.compute_zscore(data, slope, intercept)
        self.zscores.append(zscore)

        ######################################################
        # 3. Place orders
        self.place_orders(data, zscore)

    def compute_zscore(self, data, slope, intercept):
        """1. Compute the spread given slope and intercept.
           2. zscore the spread.
        """
        spread = (data['PEP'].price - (slope * data['KO'].price + intercept))
        self.spreads.append(spread)
        spread_wind = self.spreads[-self.window_length:]
        zscore = (spread - np.mean(spread_wind)) / np.std(spread_wind)
        return zscore

    def place_orders(self, data, zscore):
        """Buy spread if zscore is > 2, sell if zscore < .5.
        """
        if zscore >= 2.0 and not self.invested:
            self.order('PEP', int(100 / data['PEP'].price))
            self.order('KO', -int(100 / data['KO'].price))
            self.invested = True
        elif zscore <= -2.0 and not self.invested:
            self.order('KO', -int(100 / data['KO'].price))
            self.order('PEP', int(100 / data['PEP'].price))
            self.invested = True
        elif abs(zscore) < .5 and self.invested:
            self.sell_spread()
            self.invested = False

    def sell_spread(self):
        """
        decrease exposure, regardless of position long/short.
        buy for a short position, sell for a long.
        """
        ko_amount = self.portfolio.positions['KO'].amount
        self.order('KO', -1 * ko_amount)
        pep_amount = self.portfolio.positions['PEP'].amount
        self.order('PEP', -1 * pep_amount)


@batch_transform
def ols_transform(data, sid1, sid2):
    """Computes regression coefficient (slope and intercept)
    via Ordinary Least Squares between two SIDs.
    """
    p0 = data.price[sid1]
    p1 = sm.add_constant(data.price[sid2])
    slope, intercept = sm.OLS(p0, p1).fit().params

    return slope, intercept


class MultiMA(TradingAlgorithm):
    ''' This class is for learning zipline decorator only '''
    #FIXME decorator screw everything
    #https://www.quantopian.com/posts/batch-transform-testing-trailing-window-updated-minutely
    #https://www.quantopian.com/posts/code-example-multi-security-batch-transform-moving-average
    # batch transform decorator settings
    R_P = 1   # refresh_period
    W_L = 1   # window_length

    def initialize(self, properties, strategie, parameters):
        #tickers = [sid(21090), sid(698),sid(6872),sid(4415),sid(6119),\
                #sid(8229),sid(39778),sid(14328),sid(630),sid(4313)]
        self.debug    = properties.get('debug', 0)
        self.window_length = properties.get('window_length', 3)

    def handle_data(self, data):
        self.manager.update(self.portfolio, self.datetime.to_pydatetime())
        avgs = get_avg(refresh_period=1, window_length=3)
        self.logger.debug('{}: avgs: {}'.format(self.datetime, avgs))


#@batch_transform(refresh_period=R_P, window_length=W_L)
#def get_avg(datapanel, refresh_period=R_P, window_length=W_L):
@batch_transform
def get_avg(data, refresh_period=1, window_length=3):
    avgs = np.zeros(len(data))
    for ticker in data:
        avgs[ticker] = np.average(data[ticker].price)
    return avgs
