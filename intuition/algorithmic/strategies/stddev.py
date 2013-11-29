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
from zipline.transforms import MovingVWAP, MovingStandardDev


#TODO The portfolio management is included here, make it a stand alone manager
class StddevBased(TradingAlgorithm):
    def initialize(self, properties):
        self.save = properties.get('save', 0)
        self.debug = properties.get('debug', 0)
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

            # Very very low for forex
            #order_amount = self.portfolio.starting_cash / 1000

            # Open Long Position if current price is larger than the 9 day volume weighted average
            # plus 60% of the standard deviation (meaning the price has broken it's range to the
            # up-side by 10% more than the range value)
            if price > vwap_5_day + (standard_deviation * 0.6) and self.long_open is False and price < 1000:
                signals[stock] = price
                #self.order(stock, +order_amount)
                self.long_open = True
                self.long_open_price = price
                self.long_stoploss = self.long_open_price - standard_deviation * 0.6
                self.long_takeprofit = self.long_open_price + standard_deviation * 0.5
                self.logger.info('{}: Long Position Ordered'.format(self.datetime))

            # Close Long Position if takeprofit value hit

            # Note that less volatile stocks can end up hitting takeprofit at a small loss
            if price >= self.long_takeprofit and self.long_open is True:
                signals[stock] = -price
                #self.order(stock, -order_amount)
                self.long_open = False
                self.long_takeprofit = 0
                #profit = (price * order_amount) - (self.long_open_price * order_amount)
                self.successes = self.successes + 1
                #self.logger.info('Long Position Closed by Takeprofit at ${} profit'.format(profit))
                self.logger.info('Total Equity now at ${}'.format(equity))
                self.logger.info('So far you have had {} successful trades and {} failed trades'.format(self.successes, self.fails))
                self.logger.info('That leaves you with a winning percentage of {} percent'.format(winning_percentage))

            # Close Long Position if stoploss value hit
            if price <= self.long_stoploss and self.long_open is True:
                #self.order(stock, -order_amount)
                signals[stock] = -price
                self.long_open = False
                self.long_stoploss = 0
                #profit = (price * order_amount) - (self.long_open_price * order_amount)
                self.fails = self.fails + 1
                #self.logger.info('Long Position Closed by Stoploss at ${} profit'.format(profit))
                self.logger.info('Total Equity now at ${}'.format(equity))
                self.logger.info('So far you have had {} successful trades and {} failed trades'.format(self.successes, self.fails))
                self.logger.info('That leaves you with a winning percentage of {} percent'.format(winning_percentage))

            # Pull Plug?
            if equity < self.portfolio.starting_cash * 0.7:
                self.plug_pulled = True
                self.logger.info("Ouch! We've pulled the plug...")

            if self.plug_pulled is True and self.long_open is True:
                signals[stock] = -price
                #self.order(stock, -order_amount)
                self.long_open = False
                self.long_stoploss = 0
        ''' ----------------------------------------------------------   Orders  --'''
        if signals:
            orderBook = self.manager.trade_signals_handler(signals)
            for ticker in orderBook:
                if self.debug:
                    self.logger.notice('{} Ordering {} {} stocks'
                            .format(self.datetime, ticker, orderBook[ticker]))
                self.order(ticker, orderBook[ticker])
