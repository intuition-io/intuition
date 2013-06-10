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


from zipline.algorithm import TradingAlgorithm
import statsmodels.api as sm
from zipline.transforms import batch_transform
import numpy as np


#TODO Should handle in parameter all of the set_*
#TODO stop_trading or process_instruction are common methods
class BuyAndHold(TradingAlgorithm):
    '''Simpliest algorithm ever, just buy a stock at the first frame'''
    #NOTE test of a new configuration passing
    def initialize(self, properties):
        #NOTE can't use it here, no self.manager yet. Issue ?
        #     Could configure every common parameters in Backtester engine
        #     and use setupe_strategie as an update
        #self.manager.setup_strategie({'commission_cost': self.commission.cost})
        self.debug = properties.get('debug', False)
        self.save = properties.get('save', False)

        self.loops = 0

    def handle_data(self, data):
        self.loops += 1
        signals = {}
        ''' ----------------------------------------------------------    Init   --'''
        if self.initialized:
            user_instruction = self.manager.update(
                    self.portfolio,
                    self.datetime.to_pydatetime(),
                    self.perf_tracker.cumulative_risk_metrics.to_dict(),
                    save=self.save,
                    widgets=False)
            self.process_instruction(user_instruction)
        else:
            # Perf_tracker need at least a turn to have an index
            self.initialized = True

        if self.loops == 2:
            ''' ------------------------------------------------------    Scan   --'''
            for ticker in data:
                signals[ticker] = data[ticker].price

        ''' ----------------------------------------------------------   Orders  --'''
        import ipdb; ipdb.set_trace()
        if signals:
            orderBook = self.manager.trade_signals_handler(signals)
            for stock in orderBook:
                if self.debug:
                    self.logger.notice('{}: Ordering {} {} stocks'.format(
                        self.datetime, stock, orderBook[stock]))
                self.order(stock, orderBook[stock])

    def process_instruction(self, instruction):
        '''
        Process orders from instruction
        '''
        if instruction:
            self.logger.info('Processing user instruction')
            if (instruction['command'] == 'order') and ('amount' in instruction):
                self.logger.error('{}: Ordering {} {} stocks'.format(
                    self.datetime, instruction['amount'], instruction['asset']))

    #NOTE self.done flag could be used to avoid in zipline waist of computation
    #TODO Anyway should find a more elegant way
    def stop_trading(self):
        ''' Convenient method to stop calling user algorithm and just finish the simulation'''
        self.logger.info('Trader out of the market')
        #NOTE Selling every open positions ?
        # Saving the portfolio in database, eventually for reuse
        self.manager.save_portfolio(self.portfolio)

        # Closing generator
        self.date_sorted.close()
        #self.set_datetime(self.sim_params.last_close)
        self.done = True


@batch_transform
def ols_transform(data):
    regression = {}
    for sid in data.price:
        prices = data.price[sid].values
        x = np.arange(1, len(prices) + 1)
        x = sm.add_constant(x, prepend=True)
        regression[sid] = sm.OLS(prices, x).fit().params
    return regression


# http://nbviewer.ipython.org/4631031
class FollowTrend(TradingAlgorithm):
    def initialize(self, properties):

        self.debug = properties.get('debug', False)
        self.save = properties.get('save', False)

        self.buy_trigger = properties.get('buy_trigger', .4)
        self.sell_trigger = properties.get('sell_trigger', -self.buy_trigger)
        self.buy_leverage = properties.get('buy_leverage', 50)
        self.sell_leverage = properties.get('sell_leverage', self.buy_leverage)

        self.ols_transform = ols_transform(
            refresh_period=properties.get('refresh_period', 1),
            window_length=properties.get('window_length', 50),
            fields='price')
        self.inter = 0
        self.slope = 0

    def handle_data(self, data):

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

        self.buy = self.sell = False

        coeffs = self.ols_transform.handle_data(data)

        if coeffs is None:
            self.record(slope=self.slope,
                    buy=self.buy,
                    sell=self.sell)
            return

        for sid in data:
            self.inter, self.slope = coeffs[sid]

            if self.slope >= self.buy_trigger:
                self.order(sid, self.slope * self.buy_leverage)
                self.buy = True
            if self.slope <= -self.sell_trigger:
                self.order(sid, self.slope * self.sell_leverage)
                self.sell = True

        self.record(slope=self.slope,
                buy=self.buy,
                sell=self.sell)


class RegularRebalance(TradingAlgorithm):

    # https://www.quantopian.com/posts/global-minimum-variance-portfolio?c=1
    # For this example, we're going to write a simple momentum script.  When the 
    # stock goes up quickly, we're going to buy; when it goes down quickly, we're
    # going to sell.  Hopefully we'll ride the waves.

    # To run an algorithm in Quantopian, you need two functions: initialize and 
    # handle_data.


    def initialize(self, properties):
  
        self.debug = properties.get('debug', False)
        self.save = properties.get('save', False)

        #This is the lookback window that the entire algorithm depends on in days
        self.refresh_period = properties.get('refresh_period', 10)
        self.returns_transform = get_past_returns(
                refresh_period=self.refresh_period,
                window_length=properties.get('window_length', 40),
                compute_only_full=False)

        #Set day
        self.day = 0
     
        # Set Max and Min positions in security
        self.max_notional = 1000000.1
        self.min_notional = -1000000.0
        #Set commission
        #self.set_commission(commission.PerTrade(cost=7.95))

    def handle_data(self, data):

        self.day += 1

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

        #get 20 days of prices for each security
        daily_returns = self.returns_transform.handle_data(data)

        #circuit breaker in case transform returns none
        if daily_returns is None:
            return
        #circuit breaker, only calculate every 20 days
        if self.day % self.refresh_period is not 0:
            return

        #reweight portfolio
        for i, sid in enumerate(data):
            signals[sid] = data[sid].price

        self.process_signals(signals, historical_prices=daily_returns)

    def process_signals(self, signals, **kwargs):
        if not signals:
            return

        order_book = self.manager.trade_signals_handler(
                signals, kwargs)

        for sid in order_book:
            if self.debug:
                self.logger.notice('{} Ordering {} {} stocks'
                        .format(self.datetime, sid, order_book[sid]))
            self.order(sid, order_book[sid])


@batch_transform
def get_past_returns(data):
    '''
    Parameters: data
        pandas.panel (major: index, minor: sids)
    '''
    returns_df = data['price'].pct_change()
    #returns_df = returns_df.fillna(0.0)
    # Because of return calculation, first raw is nan
    #FIXME nan values remain anyway
    return np.nan_to_num(returns_df.values[1:])
