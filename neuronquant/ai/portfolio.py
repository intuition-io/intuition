import abc
import json
from logbook import Logger


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
        self.log = Logger('Manager')
        self.portfolio       = None
        self.date            = None
        self._optimizer_parameters = parameters
        self.connected = False
        self.server = parameters.get('server', None)
        #TODO Message emission only if a client exists ? Could try to bind and give up if no connections
        #NOTE Non blocking recv(): https://github.com/zeromq/pyzmq/issues/132   /  zmq.NOBLOCK ?
        #NOTE good example: http://zguide2.zeromq.org/py:peering3
        #if self.server.ports is not None:
            #startup_msg = self.server.receive()
            #self.connected = True
            #log.info(json.dumps(startup_msg, indent=4, separators=(',', ': ')))
        #TODO Should send stuff anyway, and accept new connections while running
        #else:

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
        #FIXME A generic method: f(ndict) = dict()
        portfolio.capital_used = portfolio.capital_used[0]
        #portfolio.start_date = portfolio.start_date.strftime(format='%Y-%m-%d %H:%M')
        #FIXME remote console receives nothing
        if self.connected:
            self.server.send({'positions': json.loads(str(portfolio.positions).replace('Position(', '').replace(')', '').replace("'", '"')),
                              'value': portfolio.portfolio_value,
                              'cash': portfolio.cash,
                              'returns': portfolio.returns,
                              'pnl': portfolio.pnl,
                              'capital_used': portfolio.capital_used,
                              'actif': portfolio.positions_value},
                              type='portfolio',
                              channel='dashboard')

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

        # Building orders for zipline
        for t in alloc:
            # Handle allocation returned as number of stocks to order
            if isinstance(alloc[t], int):
                orderBook[t] = alloc[t]

            # Handle allocation returned as stock weights to order
            elif isinstance(alloc[t], float):
                # Sell orders
                if alloc[t] <= 0:
                    orderBook[t] = int(alloc[t] * self.portfolio.positions[t].amount)
                # Buy orders
                else:
                    # If we already trade this ticker, substract owned amount before computing number of stock to buy
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
