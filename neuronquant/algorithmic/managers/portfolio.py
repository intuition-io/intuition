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


import abc
import logbook
import json

from neuronquant.data.datafeed import DataFeed
from neuronquant.tmpdata.remote import Remote
from neuronquant.utils import to_dict

import zipline.protocol as zp

from neuronquant.network.dashboard import Dashboard

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


#FIXME Extractor is for test purpose, data module will change
class PortfolioManager(object):
    '''
    Manages portfolio during simulation, and stays aware of the situation
    through the update() method. It is configured through zmq message (manager
    field) or QuanTrade/config/managers.json file.

    User strategies call it with a dictionnnary of detected opportunities (i.e.
    buy or sell signals).  Then the optimize function computes assets
    allocation, returning a dictionnary of symbols with their weigths or amount
    to reallocate.
                                  __________________________      _____________
    signals {'google': 745.5} --> |                         | --> |            |
                                  | trade_signals_handler() |     | optimize() |
    orders  {'google': 34}    <-- |_________________________| <-- |____________|

    In addition, portfolio objects can be saved in database and reloaded later,
    and user on-the-fly orders are catched and executed in remote mode. Finally
    portfolios are connected to the server broker and, if requested, send state
    messages to client.

    This is abstract class, inheretid class will eventally overwrite optmize()
    to expose their own asset allocation strategy.
    '''

    __metaclass__ = abc.ABCMeta

    #TODO Add in the constructor or setup parameters some general settings like maximum weights, positions, frequency,...
    #TODO Better to return 0 stocks to trade: remove the field
    def __init__(self, configuration):
        '''
        Parameters
            configuration : dict
                Named parameters used either for general portfolio settings
                (server and constraints), and for user optimizer function
        '''
        super(PortfolioManager, self).__init__()
        self.log       = logbook.Logger('Manager')

        # Easy mysql access
        self.datafeed  = DataFeed()

        # Zipline portfolio object, updated during simulation with self.date
        self.portfolio = None
        self.date      = None

        # Portfolio owner, mainly use for database saving and client communication
        self.name      = configuration.get('name', 'ChuckNorris')

        # Other parameters are used in user optimize() method
        self._optimizer_parameters = configuration

        # Make the manager talk to connected clients
        self.connected = configuration.get('connected', False)
        # Send android notifications when orders are processed
        # It's only possible with a running server
        self.android   = configuration.get('android', False) & self.connected

        # Delete from database data with the same portfolio name
        if configuration.get('clean', True):
            self.log.info('Cleaning previous trades.')
            clean_previous_trades(self.name)

        # Run the server if the engine didn't, while it is asked for
        if 'server' in configuration and self.connected:
            # Getting server object instanciated anyway before (by Setup object)
            self.server = configuration.pop('server')

        # Web based dashboard where real time results are monitored (test: Sandbox<br>)
        self.dashboard = Dashboard(self.name)

        # In case user optimization would need to retrieve more data
        self.remote = Remote()

    @abc.abstractmethod
    def optimize(self):
        '''
        Users should overwrite this method
        '''
        pass

    def update(self, portfolio, date, metrics=None, save=False, widgets=False):
        '''
        Actualizes the portfolio universe
        and if connected, sends it through the wires
        ________________________________
        Parameters
            portfolio: zipline.portfolio
                ndict object storing portfolio values at the given date
            date: datetime.datetime
                Current date in zipline simulation
            save: boolean
                If true, save the portfolio in database under self.name key
        '''
        # Make the manager aware of current simulation portfolio and date
        self.portfolio = portfolio
        self.date      = date

        if save:
            self.save_portfolio(portfolio)
            if metrics is not None:
                save_metrics_snapshot(self.name, self.date, metrics)

        # Delete sold items and add new ones on dashboard
        if widgets:
            self.dashboard.update_position_widgets(self.portfolio.positions)


        # Send portfolio object to client
        if self.connected:
            #NOTE Something smarter ?
            # We need to translate zipline portfolio and position objects into json data (i.e. dict)
            packet_portfolio = to_dict(portfolio)
            for pos in packet_portfolio['positions']:
                packet_portfolio['positions'][pos] = to_dict(packet_portfolio['positions'][pos])

            self.server.send(packet_portfolio,
                             type   ='portfolio',
                             channel='dashboard')

            # Check user remote messages and return it
            return self.catch_messages()
        return dict()

    def trade_signals_handler(self, signals, extras={}):
        '''
        Process buy and sell signals from the simulation
        ___________________________________________________________
        Parameters
            signals: dict
                hold stocks of interest, format like {"google": 567.89, "apple": -345.98}
                If the value is negative -> sell signal, otherwize buy one
            extras: whatever
                Object sent from algorithm for certain managers
        ___________________________________________________________
        Return
            dict orderBook, like {"google": 34, "apple": -56}
        '''
        self._optimizer_parameters['algo'] = extras
        orderBook       = dict()

        # If value < 0, it's a sell signal on the key, else buy signal
        to_buy          = [t for t in signals if signals[t] > 0]
        to_sell         = set(self.portfolio.positions.keys()).intersection([t for t in signals if signals[t] < 0])
        if not to_buy and not to_sell:
            # Nothing to do
            return dict()

        # Compute the optimal portfolio allocation, using user defined function
        alloc, e_ret, e_risk = self.optimize(self.date, to_buy, to_sell, self._optimizer_parameters)

        #TODO Check about selling in available money and handle 250 stocks limit
        #TODO Handle max_* as well, ! already actif stocks

        ## Building orders for zipline
        #NOTE The follonwing in a separate function that could be used when catching message from user
        for t in alloc:
            ## Handle allocation returned as number of stocks to order
            if isinstance(alloc[t], int):
                orderBook[t] = alloc[t]

            ## Handle allocation returned as stock weights to order
            elif isinstance(alloc[t], float):
                # Sell orders
                if alloc[t] <= 0:
                    orderBook[t] = int(alloc[t] * self.portfolio.positions[t].amount)
                ## Buy orders
                else:
                    ## If we already trade this ticker, substract owned amount before computing number of stock to buy
                    if self.portfolio.positions[t].amount:
                        price = self.portfolio.positions[t].last_sale_price
                    else:
                        price = signals[t]
                    orderBook[t] = (int(alloc[t] * self.portfolio.portfolio_value / price)
                                    - self.portfolio.positions[t].amount)

        if self.android and orderBook:
            # Alert user of the orders about to be processed
            # Ok... kind of fancy method
            ords = {'-1': 'sell', '1': 'buy'}
            msg = 'QuanTrade suggests you to '
            msg += ', '.join(['{} {} stocks of {}'
                .format(ords[str(amount / abs(amount))], amount, ticker) for
                ticker, amount in orderBook.iteritems()])
            self.server.send_to_android({'title': 'Portfolio manager notification',
                                         'priority': 1,
                                         'description': msg})

        return orderBook

    def setup_strategie(self, parameters):
        '''
        General parameters or user settings
        (maw_weigth, max_assets, max_frequency, commission cost)
        ________________________________________________________
        Parameters
            parameters: dict
                Arbitrary values to change general constraints,
                or for user algorithm settings
        '''
        assert isinstance(parameters, dict)
        for name, value in parameters.iteritems():
            self._optimizer_parameters[name] = value

    def save_portfolio(self, portfolio):
        '''
        Store in database given portfolio,
        for reuse later or further analysis puropose
        ____________________________________________
        Parameters
            portfolio: zipline.protocol.Portfolio(1)
                ndict portfolio object to store
        ___________________________________________
        '''
        self.log.info('Saving portfolio in database')
        self.datafeed.stock_db.save_portfolio(portfolio, self.name, self.date)

    def load_portfolio(self, name):
        '''
        Load a complete portfolio object from database
        ______________________________________________
        Parameters
            name: str(...)
                name used as primary key in db for the portfolio
        ______________________________________________
        Return
            The portfolio with the given name if found,
            None otherwize
        '''
        self.log.info('Loading portfolio from database')
        # Get the portfolio as a pandas Serie
        db_pf = self.datafeed.saved_portfolios(name)

        # Create empty Portfolio object to be filled
        portfolio = zp.Portfolio()

        # The function returns an empty dataframe if it didn't find a portfolio with id 'name' in db
        if len(db_pf):
            # Fill new portfolio data structure
            portfolio.capital_used    = db_pf['Capital']
            portfolio.starting_cash   = db_pf['StartingCash']
            portfolio.portfolio_value = db_pf['PortfolioValue']
            portfolio.pnl             = db_pf['PNL']
            portfolio.returns         = db_pf['Returns']
            portfolio.cash            = db_pf['Cash']
            portfolio.start_date      = db_pf['StartDate']
            portfolio.positions       = self._adapt_positions_type(db_pf['Positions'])
            portfolio.positions_value = db_pf['PositionsValue']

        return portfolio

    def _adapt_positions_type(self, db_pos):
        '''
        From array of sql Positions data model
        To Zipline Positions object
        '''
        # Create empty Positions object to be filled
        positions = zp.Positions()

        for pos in db_pos:
            if pos.Ticker not in positions:
                positions[pos.Ticker] = zp.Position(pos.Ticker)
            position = positions[pos.Ticker]
            position.amount = pos.Amount
            position.cost_basis = pos.CostBasis
            position.last_sale_price = pos.LastSalePrice

        return positions

    def catch_messages(self, timeout=1):
        '''
        Listen for user messages,
        process usual orders
        '''
        msg = self.server.noblock_recv(timeout=timeout, json=True)
        #TODO msg is a command or an information, process it
        if msg:
            self.log.info('Got message from user: {}'.format(msg))
            try:
                msg = json.loads(msg)
            except:
                msg = ''
                self.log.error('Unable to parse user message')
        return msg
