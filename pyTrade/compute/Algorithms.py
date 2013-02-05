import datetime
import pytz
import numpy as np
import sys
import os

sys.path.append(str(os.environ['ZIPLINE']))
from zipline.algorithm import TradingAlgorithm
from zipline.transforms import MovingAverage, MovingVWAP
#from zipline.transforms import batch_transform

sys.path.append(str(os.environ['QTRADE']))
from pyTrade.ai.manager import PortfolioManager

from logbook import Logger
import ipdb as pdb


#TODO Override initialiez function with portfolio, logger and parameters initialization
#TODO Should handle in parameter all of the set_*
class BuyAndHold(TradingAlgorithm):
    '''Simpliest algorithm ever, just buy a stock at the first frame'''
    def initialize(self, properties, strategie, parameters):
        self.set_logger(Logger('Algorithm'))
        self.manager = PortfolioManager(self.commission.cost)
        self.manager.setup_strategie(strategie, parameters)

    def handle_data(self, data):
        ''' ----------------------------------------------------------    Init   --'''
        self.frame_count += 1
        self.manager.update(self.portfolio, self.datetime.to_pydatetime())
        signals = dict()

        ''' ----------------------------------------------------------    Scan   --'''
        if self.frame_count == 2:
            for ticker in data:
                signals[ticker] = data[ticker].price

        ''' ----------------------------------------------------------   Orders  --'''
        if signals:
            orderBook = self.manager.trade_signals_handler(signals)
            for order in orderBook:
                self.order(order, orderBook[order])


class DualMovingAverage(TradingAlgorithm):
    """Dual Moving Average Crossover algorithm.
    This algorithm buys apple once its short moving average crosses
    its long moving average (indicating upwards momentum) and sells
    its shares once the averages cross again (indicating downwards
    momentum).
    """
    def initialize(self, properties, strategie, parameters):
        short_window       = properties.get('short_window', 200)
        long_window        = properties.get('long_window', 400)
        self.amount        = properties.get('amount', 10000)
        self.threshold     = properties.get('threshold', 0)
        #self.capital_base = properties.get('capital_base', 1000)
        self.debug         = properties.get('debug', True)

        self.add_transform(MovingAverage, 'short_mavg', ['price'],
                           window_length=short_window)

        self.add_transform(MovingAverage, 'long_mavg', ['price'],
                           window_length=long_window)

        # To keep track of whether we invested in the stock or not
        self.invested = {}

        self.short_mavgs = []
        self.long_mavgs = []

        self.manager = PortfolioManager(self.commission.cost)
        #self.manager.setup_strategie(strategie, loopback=parameters.get('loopback', 50), source=parameters.get('source', 'mysql'))
        self.manager.setup_strategie(strategie, parameters)

    def handle_data(self, data):
        ''' ----------------------------------------------------------    Init   --'''
        #pdb.set_trace()
        self.manager.update(self.portfolio, self.datetime.to_pydatetime())
        #self.manager.update(self.portfolio, datetime.datetime.now())
        signals = dict()
        self.frame_count += 1
        if (self.frame_count == 1):
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
                    print('Ordering {} {} stocks'.format(ticker, orderBook[ticker]))
                self.order(ticker, orderBook[ticker])

        # Save mavgs for later analysis.
        self.short_mavgs.append(short_mavg)
        self.long_mavgs.append(long_mavg)


class VolumeWeightAveragePrice(TradingAlgorithm):
    '''https://www.quantopian.com/posts/updated-multi-sid-example-algorithm-1'''
    def initialize(self, properties, strategie, parameters):
        # Common setup
        self.set_logger(Logger('Algorithm'))
        self.debug    = properties.get('debug', 0)
        window_length = properties.get('window_length', 3)
        self.manager  = PortfolioManager(self.commission.cost)
        self.manager.setup_strategie(strategie, parameters)

        # Here we initialize each stock.  Note that we're not storing integers; by
        # calling sid(123) we're storing the Security object.
        self.vwap = {}
        self.price = {}

        # Setting our maximum position size, like previous example
        self.max_notional = 1000000.1
        self.min_notional = -1000000.0

        # initializing the time variables we use for logging
        utc = pytz.timezone('UTC')
        self.d = datetime.datetime(2008, 6, 20, 0, 0, 0, tzinfo=utc)

        self.add_transform(MovingVWAP, 'vwap', market_aware=True, window_length=window_length)

    def handle_data(self, data):
        self.frame_count += 1
        signals = dict()
        self.manager.update(self.portfolio, self.datetime.to_pydatetime())

        # Initializing the position as zero at the start of each frame
        notional = 0

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

        if signals and self.datetime.to_pydatetime() > self.portfolio.start_date:
            order_book = self.manager.trade_signals_handler(signals)
            for stock in order_book:
                if self.debug:
                    self.logger.info('Ordering {} {} stocks'.format(stock, order_book[stock]))
                self.order(stock, order_book[stock])
                notional = notional + price * order_book[stock]

'''
class MultiMA(TradingAlgorithm):
    #https://www.quantopian.com/posts/batch-transform-testing-trailing-window-updated-minutely
    #https://www.quantopian.com/posts/code-example-multi-security-batch-transform-moving-average
    # batch transform decorator settings
    R_P = 1   # refresh_period
    W_L = 1   # window_length

    def initialize(self, properties):
        # Lots of sids !
        #self.stocks = [sid(21090), sid(698),sid(6872),sid(4415),sid(6119),\
                #sid(8229),sid(39778),sid(14328),sid(630),sid(4313)]
        pass

    def handle_data(self, data):
        # data AND self.stocks ??
        avgs = self.get_avg(data, self.stocks)
        event_time = data[self.stocks[0]].datetime
        self.logger.debug(event_time)
        self.logger.debug(avgs)

    @batch_transform(refresh_period=R_P, window_length=W_L)
    def get_avg(datapanel, sids):
        avgs = np.zeros(len(sids))
        for i, s in enumerate(sids):
            avgs[i] = np.average(datapanel['price'][s].values)
        return avgs
'''


class Momentum(TradingAlgorithm):
    '''
    https://www.quantopian.com/posts/this-is-amazing
    !! Many transactions, so make the algorithm explode when traded with many positions
    '''
    def initialize(self, properties, strategie, parameters):
        self.set_logger(Logger('Algorithm'))
        self.debug    = properties.get('debug', 0)
        window_length = properties.get('window_length', 3)
        self.manager = PortfolioManager(self.commission.cost)
        self.manager.setup_strategie(strategie, parameters)

        self.max_notional = 100000.1
        self.min_notional = -100000.0

        self.add_transform(MovingAverage, 'mavg', ['price'], window_length=window_length)

    def handle_data(self, data):
        self.manager.update(self.portfolio, self.datetime.to_pydatetime())
        signals = dict()
        notional = 0
        for ticker in data:
            sma          = data[ticker].mavg.price
            price        = data[ticker].price
            cash         = self.portfolio.cash
            notional     = self.portfolio.positions[ticker].amount * price
            capital_used = self.portfolio.capital_used

            # notional stuff are portfolio strategies, implement a new one, combinaison => parameters !
            #pdb.set_trace()
            if sma >= price and notional > -0.2 * (capital_used[0] + cash):
                signals[ticker] = - price
            elif sma <= price and notional < 0.2 * (capital_used[0] + cash):
                signals[ticker] = price

        if signals:
            order_book = self.manager.trade_signals_handler(signals)
            for ticker in order_book:
                self.order(ticker, order_book[ticker])
                if self.debug:
                    self.logger.info('{}: Ordering {} {} stocks'.format(self.datetime, ticker, order_book[ticker]))


class MovingAverageCrossover(TradingAlgorithm):
    '''
    https://www.quantopian.com/posts/moving-average-crossover
    '''
    def initialize(self, properties):
        self.fast = []
        self.slow = []
        self.medium = []
        self.breakoutFilter = 0

        self.passedMediumLong = False
        self.passedMediumShort = False

        self.holdingLongPosition = False
        self.holdingShortPosition = False

        self.entryPrice = 0.0

    def handle_data(data, self):
        self.fast.append(data[self.stock].price)
        self.slow.append(data[self.stock].price)
        self.medium.append(data[self.stock].price)

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
                self.order(self.stock, 100)

                self.holdingLongPosition = True
                self.breakoutFilter = 0
                self.entryPrice = data[self.stock].price
            else:
                self.breakoutFilter += 1

        if (self.holdingShortPosition is False and self.holdingLongPosition is False
                and self.passedMediumShort is True
                and ((fastMovingAverage > 0.0 and slowMovingAverage > 0.0)
                and (fastMovingAverage < mediumMovingAverage))):

            if self.breakoutFilter > 5:
                self.logger.info("ENTERING SHORT POSITION")
                self.order(self.stock, -100)
                self.holdingShortPosition = True
                self.breakoutFilter = 0
                self.entryPrice = data[self.stock].price
            else:
                self.breakoutFilter += 1

        # Exit Strategies
        if (self.holdingLongPosition is True
                    and ((fastMovingAverage > 0.0 and slowMovingAverage > 0.0)
                    and (fastMovingAverage < mediumMovingAverage))):

            if self.breakoutFilter > 5:
                self.order(self.stock, -100)
                self.holdingLongPosition = False
                self.breakoutFilter = 0
            else:
                self.breakoutFilter += 1

        if (self.holdingShortPosition is True
                and ((fastMovingAverage > 0.0 and slowMovingAverage > 0.0)
                and (fastMovingAverage > mediumMovingAverage))):
            if self.breakoutFilter > 5:
                self.order(self.stock, 100)
                self.holdingShortPosition = False
                self.breakoutFilter = 0
            else:
                self.breakoutFilter += 1


class OLMAR(TradingAlgorithm):
    def initialize(self, properties):
        # http://money.usnews.com/funds/etfs/rankings/small-cap-funds
        #self.stocks = [sid(27796),sid(33412),sid(38902),sid(21508),sid(39458),sid(25899),sid(40143),sid(21519),sid(39143),sid(26449)]
        self.m = len(self.stocks)
        self.price = {}
        self.b_t = np.ones(self.m) / self.m
        self.eps = 1.04   # Change epsilon here
        self.init = False

        self.set_slippage(self.slippage.VolumeShareSlippage(volume_limit=0.25, price_impact=0))
        self.set_commission(self.commission.PerShare(cost=0))

    def handle_data(self, data):
        if not self.init:
            self.rebalance_portfolio(self, data, self.b_t)
            self.init = True
            return

        m = self.m
        x_tilde = np.zeros(m)
        b = np.zeros(m)

        # find relative moving average price for each security
        for i, stock in enumerate(self.stocks):
            price = data[stock].price
            x_tilde[i] = float(data[stock].mavg(5)) / price   # change moving average window here

        ###########################
        # Inside of OLMAR (algo 2)

        x_bar = x_tilde.mean()

        # Calculate terms for lambda (lam)
        dot_prod = np.dot(self.b_t, x_tilde)
        num = self.eps - dot_prod
        denom = (np.linalg.norm((x_tilde - x_bar))) ** 2

        # test for divide-by-zero case
        if denom == 0.0:
            lam = 0  # no portolio update
        else:
            lam = max(0, num / denom)

        b = self.b_t + lam * (x_tilde - x_bar)
        b_norm = self.simplex_projection(b)
        self.rebalance_portfolio(self, data, b_norm)

        # update portfolio
        self.b_t = b_norm
        self.logger.debug(b_norm)

    def rebalance_portfolio(self, data, desired_port):
        #rebalance portfolio
        current_amount = np.zeros_like(desired_port)
        desired_amount = np.zeros_like(desired_port)

        if not self.init:
            positions_value = self.portfolio.starting_cash
        else:
            positions_value = self.portfolio.positions_value + self.portfolio.cash

        for i, stock in enumerate(self.stocks):
            current_amount[i] = self.portfolio.positions[stock].amount
            desired_amount[i] = desired_port[i] * positions_value / data[stock].price

        diff_amount = desired_amount - current_amount

        for i, stock in enumerate(self.stocks):
            self.order(stock, diff_amount[i])   # order_stock

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

    def handle_data(self, data):
        # Reporting Variables
        profit = 0
        total_trades = self.successes + self.fails
        winning_percentage = self.successes / total_trades * 100

        # Data Variables
        starting_cash = self.portfolio.starting_cash
        price = data[self.stock].price
        vwap_5_day = data[self.stock].vwap(5)
        equity = self.portfolio.cash + self.portfolio.positions_value
        standard_deviation = data[self.stock].stddev(9)

        # Set order size

        # (Set here as "starting_cash/1000" - which coupled with the below
        # "and price < 1000" - is a scalable way of setting (initially :P)
        # affordable order quantities (for most stocks).

        order_amount = starting_cash / 1000

        # Open Long Position if current price is larger than the 9 day volume weighted average
        # plus 60% of the standard deviation (meaning the price has broken it's range to the
        # up-side by 10% more than the range value)
        if price > vwap_5_day + (standard_deviation * 0.6) and self.long_open is False and price < 1000:
            self.order(self.stock, +order_amount)
            self.long_open = True
            self.long_open_price = price
            self.long_stoploss = self.long_open_price - standard_deviation * 0.6
            self.long_takeprofit = self.long_open_price + standard_deviation * 0.5
            print 'Long Position Ordered'

        # Close Long Position if takeprofit value hit

        # Note that less volatile stocks can end up hitting takeprofit at a small loss
        if price >= self.long_takeprofit and self.long_open is True:
            self.order(self.stock, -order_amount)
            self.long_open = False
            self.long_takeprofit = 0
            profit = (price * order_amount) - (self.long_open_price * order_amount)
            self.successes = self.successes + 1
            print 'Long Position Closed by Takeprofit at $%d profit' % (profit)
            print 'Total Equity now at $%d' % (equity)
            print 'So far you have had %d successful trades and %d failed trades' % (self.successes, self.fails)
            print 'That leaves you with a winning percentage of %d percent' % (winning_percentage)

        # Close Long Position if stoploss value hit
        if price <= self.long_stoploss and self.long_open is True:
            self.order(self.stock, -order_amount)
            self.long_open = False
            self.long_stoploss = 0
            profit = (price * order_amount) - (self.long_open_price * order_amount)
            self.fails = self.fails + 1
            print 'Long Position Closed by Stoploss at $%d profit' % (profit)
            print 'Total Equity now at $%d' % (equity)
            print 'So far you have had %d successful trades and %d failed trades' % (self.successes, self.fails)
            print 'That leaves you with a winning percentage of %d percent' % (winning_percentage)

        # Pull Plug?
        if equity < starting_cash * 0.7:
            self.plug_pulled = True
            print "Ouch! We've pulled the plug..."

        if self.plug_pulled is True and self.long_open is True:
            self.order(self.stock, -order_amount)
            self.long_open = False
            self.long_stoploss = 0
