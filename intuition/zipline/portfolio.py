#
# Copyright 2013 Xavier Bruhiere
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

import intuition.data.remote as remote
#FIXME Insights is an optional depency !!
#import insights.plugins.mobile as mobile


class PortfolioFactory():
    '''
    Manages portfolio during simulation, and stays aware of the situation
    through the update() method.

    User strategies call it with a dictionnnary of detected opportunities (i.e.
    buy or sell signals).  Then the optimize function computes assets
    allocation, returning a dictionnary of symbols with their weigths or amount
    to reallocate.
                                  __________________________      _____________
    signals {'google': 745.5} --> |                         | -> |            |
                                  | trade_signals_handler() |    | optimize() |
    orders  {'google': 34}    <-- |_________________________| <- |____________|

    In addition, portfolio objects can be saved in database and reloaded later,
    and user on-the-fly orders are catched and executed in remote mode. Finally
    portfolios are connected to the server broker and, if requested, send state
    messages to client.

    This is abstract class, inheretid class will eventally overwrite optmize()
    to expose their own asset allocation strategy.
    '''

    __metaclass__ = abc.ABCMeta

    # Zipline portfolio object, updated during simulation with self.date
    portfolio = None
    perfs = None
    date = None
    bullet = None

    #TODO Add in the constructor or setup parameters some general settings like
    #     maximum weights, positions, frequency, ...
    #TODO Better to return 0 stocks to trade: remove the field
    #NOTE Regarding portfolio constraints: from a set of user-defined
    # parameters, a unique set should be constructed. Then the solution
    # provided by optimize function would have to be a subset of it. (classic
    # mathematical solution) Finally it should be defined how to handle
    # non-correct solutions
    def __init__(self, configuration):
        '''
        Parameters
            configuration : dict
                Named parameters used either for general portfolio settings
                (server and constraints), and for user optimizer function
        '''
        # Portfolio owner, mainly used for database saving and client
        # communication
        self.log = logbook.Logger('intuition.portfolio')

        # Other parameters are used in user's optimize() method
        self._optimizer_parameters = configuration

        # Make the manager talk to connected clients
        self.connected = configuration.get('connected', False)
        # Send android notifications when orders are processed
        #device = configuration.get('device', '')
        #if device:
            #self.bullet = mobile.AndroidPush(device)

        # Run the server if the engine didn't, while it is asked for
        if 'server' in configuration and self.connected:
            # Getting server object instanciated anyway before
            self.server = configuration.pop('server')

        # In case user optimization would need to retrieve more data
        self.data = remote.Data()
        self.initialize(configuration)

    def initialize(self, configuration):
        ''' Users should overwrite this method '''
        pass

    @abc.abstractmethod
    def optimize(self, date, to_buy, to_sell, parameters):
        ''' Users should overwrite this method '''
        pass

    def update(self, portfolio, date, perfs=None):
        '''
        Actualizes the portfolio universe
        ________________________________
        Parameters
            portfolio: zipline.Portfolio
                ndict object storing portfolio values at the given date
            date: datetime.datetime
                Current date in zipline simulation
        '''
        # Make the manager aware of current simulation
        self.portfolio = portfolio
        self.perfs = perfs
        self.date = date

    def trade_signals_handler(self, signals, extras={}):
        '''
        Process buy and sell signals from the simulation
        ___________________________________________________________
        Parameters
            signals: dict
                hold stocks of interest, format: {"google": 0.8, "apple": -0.2}
                If the value is negative -> sell signal, otherwize buy one
                Values are ranged between [-1 1] regarding signal confidence
            extras: whatever
                Object sent from algorithm for certain managers
        ___________________________________________________________
        Return
            dict order_book, like {"google": 34, "apple": -56}
        '''

        self._optimizer_parameters['algo'] = extras
        order_book = {}

        # If value < 0, it's a sell signal on the key, else buy signal
        to_buy = dict(filter(lambda (sid, strength):
                             strength > 0, signals.iteritems()))
        to_sell = dict(filter(lambda (sid, strength):
                              strength < 0, signals.iteritems()))
        #to_buy    = [t for t in signals if signals[t] > 0]
        #NOTE With this line we can't go short
        #to_sell   = set(self.portfolio.positions.keys()).intersection(
                #[t for t in signals if signals[t] < 0])

        if not to_buy and not to_sell:
            # Nothing to do
            return {}

        # Compute the optimal portfolio allocation, using user defined function
        alloc, e_ret, e_risk = self.optimize(
            self.date, to_buy, to_sell, self._optimizer_parameters)

        #TODO Check about selling within available money
        #     and handle 250 stocks limit
        #TODO Handle max_* as well, ! already actif stocks

        ## Building orders for zipline
        #NOTE The follonwing in a separate function that could be used when
        #     catching message from user
        for t in alloc:
            ## Handle allocation returned as number of stocks to order
            if isinstance(alloc[t], int):
                order_book[t] = alloc[t]

            ## Handle allocation returned as stock weights to order
            elif isinstance(alloc[t], float):
                # Sell orders
                if alloc[t] <= 0:
                    order_book[t] = int(alloc[t] *
                                        self.portfolio.positions[t].amount)
                ## Buy orders
                else:
                    # If we already trade this ticker, substract owned amount
                    # before computing number of stock to buy
                    if self.portfolio.positions[t].amount:
                        price = self.portfolio.positions[t].last_sale_price
                    else:
                        price = signals[t]
                    order_book[t] = (int(alloc[t] *
                                     self.portfolio.portfolio_value / price)
                                     - self.portfolio.positions[t].amount)

        '''
        if self.bullet and order_book:
            # Alert user of the orders about to be processed
            # Ok... kind of fancy method
            ords = {'-1': 'You should sell', '1': 'You should buy'}
            items = ['{} {} stocks of {}'.format(
                ords[str(amount / abs(amount))], amount, ticker)
                for ticker, amount in order_book.iteritems()]
            payload = {
                'title': 'Portfolio manager notification',
                'items': items,
            }
            req = self.bullet.push(payload)
            self.log.debug(req)
        '''

        return order_book

    def advise(self, **kwargs):
        '''
        General parameters or user settings
        (maw_weigth, max_assets, max_frequency, commission cost)
        ________________________________________________________
        Parameters
            parameters: dict
                Arbitrary values to change general constraints,
                or for user algorithm settings
        '''
        for name, value in kwargs.iteritems():
            self._optimizer_parameters[name] = value

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
