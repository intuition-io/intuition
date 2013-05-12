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

from neuronquant.network.dashboard import Dashboard
dashboard = Dashboard('Sandbox<br>')

from neuronquant.tmpdata.extractor import Extractor
extractor = Extractor('mysql://xavier:quantrade@localhost/stock_data')
metrics_fields = ['Information', 'Returns', 'MaxDrawdown', 'SortinoRatio', 'Period', 'Volatility', 'BenchmarkVolatility', 'Beta', 'ExcessReturn', 'TreasuryReturns', 'SharpeRatio', 'Date', 'Alpha', 'BenchmarkReturns', 'Name']


def save_metrics_snapshot(name, dt, cmr):
    #TODO Save Transactions
    #data = extractor('INSERT INTO Transactions () VALUES ()')
    #TODO Save Orders
    #data = extractor('INSERT INTO Orders () VALUES ()')
    # Save Cumulative risk metrics
    #NOTE Simple self.datetime enough ?
    cmr['date'] = "'{}'".format(dt.strftime(format='%Y-%m-%d %H:%M'))
    cmr['period_label'] = "'{}-30'".format(cmr['period_label'])
    cmr['name'] = "'" + name + "'"
    cmr.pop('trading_days')
    for key in cmr:
        #NOTE if isinstance(type(cmr[key]), float): cmr[key] = round(cmr[key], 4)
        if cmr[key] is None:
            cmr[key] = 0
    query = 'INSERT INTO Metrics ({}) VALUES ({})'
    extractor(query.format(', '.join(metrics_fields), ', '.join(map(str, cmr.values()))))


def clean_previous_trades(portfolio_name):
    extractor('DELETE FROM Positions WHERE PortfolioName=\'{}\''.format(portfolio_name))
    extractor('DELETE FROM Portfolios where Name=\'{}\''.format(portfolio_name))
    extractor('DELETE FROM Metrics where Name=\'{}\''.format(portfolio_name))
    #TODO Clean previous widgets


def update_positions_widgets(previous_positions, current_positions):
    for stock in current_positions:
        amount = current_positions[stock].amount
        stock = stock.replace(' ', '+')
        if (amount == 0) and (stock in previous_positions):
            previous_positions.pop(stock)
            dashboard.del_widget(stock)
        if (amount != 0) and (stock not in previous_positions):
            previous_positions[stock] = amount
            dashboard.add_number_widget(
                    {'name': stock,
                     'source': 'http_proxy',
                     'proxy_url': 'http://127.0.0.1:8080/dashboard/number?data=Amount&table=Positions&field=Ticker&value={}'.format(stock),
                     'proxy_value_path': ' ',
                     'label': '$',
                     'update_interval': '30',
                     'use_metrics_suffix': True})
    #NOTE previous_positions is a pointer in python so no need to return ?
    return previous_positions


#TODO The portfolio management is included here, make it a stand alone manager
class StddevBased(TradingAlgorithm):
    def initialize(self, properties):
        self.save = properties.get('save', 0)
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
            user_instruction = self.manager.update(self.portfolio, self.datetime.to_pydatetime(), save=self.save)
            save_metrics_snapshot(self.manager.name,
                                     self.datetime.to_pydatetime(),
                                     self.perf_tracker.cumulative_risk_metrics.to_dict())

            update_positions_widgets(self.previous_positions, self.portfolio.positions)
        else:
            #TODO Obviously the manager should clean by himself
            clean_previous_trades(self.manager.name)
            self.initialized = True
            self.previous_positions = {}

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
