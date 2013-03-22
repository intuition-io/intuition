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
from logbook import Logger

from neuronquant.data.datafeed import DataFeed
from neuronquant.utils import to_dict

import zipline.protocol as zp


class PortfolioManager:
    '''
    Observes the trader universe and produces
    orders to be excuted within zipline
    Abstract method meant to be used by user
    to construct their portfolio optimizer
    '''
    __metaclass__ = abc.ABCMeta

    #TODO Add in the constructor or setup parameters some general settings like maximum weights, positions, frequency,...
    def __init__(self, parameters):
        '''
        Parameters
            parameters : dict(...)
                Named parameters used either for general portfolio settings
                (server and constraints), and for user optimizer function
        '''
        super(PortfolioManager, self).__init__()
        self.log       = Logger('Manager')
        self.datafeed      = DataFeed()
        self.portfolio = None
        self.date      = None
        self.name      = parameters.get('name', 'Chuck Norris')
        self._optimizer_parameters = parameters
        self.connected = False
        self.server = parameters.get('server', None)
        #TODO Should send stuff anyway, and accept new connections while running

        self.connected = parameters.get('connected', False)

        # Run the server if the engine didn't while it is asked
        if self.server.port is None and self.connected:
            self.log.info('Binding manager on default port...')
            self.server.run(host='127.0.0.1', port=5570)

    @abc.abstractmethod
    def optimize(self):
        '''
        Users must overwrite this method
        '''
        pass

    def update(self, portfolio, date):
        '''
        Actualizes the portfolio universe
        and if connected, sends it through the wires
        ________________________________
        Parameters
            portfolio: zipline.portfolio(1)
                ndict object storing portfolio values at the given date
            date: datetime.datetime(1)
                Current date in zipline simulation
        '''
        self.portfolio = portfolio
        self.date      = date

        if self.connected:
            self.server.send(to_dict(portfolio),
                              type    = 'portfolio',
                              channel = 'dashboard')

            return self.catch_messages()
        return dict()

    def trade_signals_handler(self, signals):
        '''
        Process buy and sell signals from backtester or live trader
        @param signals: dict holding stocks of interest, format like {"google": 567.89, "apple": -345.98}
                       If the value is negative -> sell signal, otherwize buy one
        @return: dict orderBook, like {"google": 34, "apple": -56}
        '''
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

        return orderBook

    def setup_strategie(self, parameters):
        '''
        General parameters or user ones setting
        (maw_weigth, max_assets, max_frequency, commission cost)
        ________________________________________________________
        Parameters
            parameters: dict(...)
                Arbitrary values to change general constraints,
                or for user algorithm settings
        '''
        for name, value in parameters.iteritems():
            self._optimizer_parameters[name] = value

    #TODO Still need here this dict = f(ndict)
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
        ## Get the portfolio as a pandas Serie
        db_pf = self.datafeed.saved_portfolios(name)
        ## The function returns None if it didn't find a portfolio with id 'name' in db
        if db_pf is None:
            return None

        # Creating portfolio object
        portfolio = zp.Portfolio()

        portfolio.capital_used = db_pf['Capital']
        portfolio.starting_cash = db_pf['StartingCash']
        portfolio.portfolio_value = db_pf['PortfolioValue']
        portfolio.pnl = db_pf['PNL']
        portfolio.returns = db_pf['Returns']
        portfolio.cash = db_pf['Cash']
        portfolio.start_date = db_pf['StartDate']
        portfolio.positions = self._adapt_positions_format(db_pf['Positions'])
        portfolio.positions_value = db_pf['PositionsValue']

        return portfolio

    def _adapt_positions_type(self, db_pos):
        '''
        From array of sql Positions data model
        To Zipline Positions object
        '''
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
        return msg
