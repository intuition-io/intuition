import ipdb as pdb

import os
import sys
import json
import signal

import pytz
import pandas as pd

from logbook import Logger

log = Logger('Manager')

app_path = os.environ['QTRADE']
sys.path.append(app_path)
portfolio_opt_file = '/'.join((app_path, 'neuronquant/ai/opt_utils.R'))
#from pyTrade.data.datafeed import DataFeed

import rpy2.robjects as robjects
r = robjects.r


class PortfolioManager(object):
    '''
    This class observes the trader universe and makes orders
    @param positions : list holding active positions like ["google", "apple"]
    @param level     : verbose level
    '''
    #TODO Add in the constructor or setup parameters some general settings like maximum weights, positions, frequency,...
    def __init__(self, parameters):
        super(PortfolioManager, self).__init__()
        #self.feeds           = DataFeed()
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
        if self.server.port is None:
            log.info('Binding manager on default port...')
            self.server.run(host='127.0.0.1', port=5570)
        r('source("{}")'.format(portfolio_opt_file))

    def optimize(self):
        ''' Users must overwrite this method '''
        pass

    def update(self, portfolio, date):
        self.portfolio = portfolio
        self.date      = date
        #FIXME A generic method: f(ndict) = dict()
        portfolio.capital_used = portfolio.capital_used[0]
        #portfolio.start_date = portfolio.start_date.strftime(format='%Y-%m-%d %H:%M')
        try:
            self.server.send({'portfolio': {
                              'positions': json.loads(str(portfolio.positions).replace('Position(', '').replace(')', '').replace("'", '"')),
                              'value': portfolio.portfolio_value,
                              'cash': portfolio.cash,
                              'returns': portfolio.returns,
                              'pnl': portfolio.pnl,
                              'capital_used': portfolio.capital_used,
                              'actif': portfolio.positions_value}},
                             channel='dashboard')
            #log.info(json.dumps(response, indent=4, separators=(',', ': ')))
        except:
            log.error('** Sending portfolio snapshot to client')

    def trade_signals_handler(self, signals):
        '''
        Process buy and sell signals from backtester or live trader
        @param signals: dict holding stocks of interest, format like {"google": 567.89, "apple": -345.98}
                       If the value is negative -> sell signal, otherwize buy one
        @return: dict orderBook, like {"google": 34, "apple": -56}
        '''
        orderBook       = dict()
        to_buy          = [t for t in signals if signals[t] > 0]
        to_sell         = set(self.portfolio.positions.keys()).intersection([t for t in signals if signals[t] < 0])
        if not to_buy and not to_sell:
            return dict()

        alloc, e_ret, e_risk = self.optimize(self.date, to_buy, to_sell, self._optimizer_parameters)

        #TODO Check about selling in available money and handle 250 stocks limit
        #TODO Handle max_* as well, ! already actif stocks
        #for t in dict((k, v) for (k, v) in alloc.iteritems() if v < 0):
        for t in alloc:
            if isinstance(alloc[t], int):
                orderBook[t] = alloc[t]
            elif isinstance(alloc[t], float):
                if alloc[t] <= 0:
                    orderBook[t] = int(alloc[t] * self.portfolio.positions[t].amount)
                else:
                    try:
                        orderBook[t] = int(alloc[t] * self.portfolio.portfolio_value / signals[t]) - self.portfolio.positions[t].amount
                    except:
                        # In old_manager.py signals[t] was not used, an issue i forgot ?
                        pdb.set_trace()

        return orderBook

    def setup_strategie(self, parameters):
        ''' General parameters (maw_weigth, max_assets, max_frequency, commission cost) '''
        for name, value in parameters.iteritems():
            self._optimizer_parameters[name] = value
