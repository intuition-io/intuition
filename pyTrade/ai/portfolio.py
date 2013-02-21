import ipdb as pdb

import os
import sys

import pytz
import pandas as pd

from logbook import Logger

log = Logger('Manager')

app_path = os.environ['QTRADE']
sys.path.append(app_path)
portfolio_opt_file = '/'.join((app_path, 'pyTrade/ai/opt_utils.R'))
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
        self.server = parameters.get('server', None)
        r('source("{}")'.format(portfolio_opt_file))

    def optimize(self):
        ''' Users must overwrite this method '''
        pass

    def update(self, portfolio, date):
        self.portfolio = portfolio
        self.date      = date
        self.server.socket.send(str(portfolio)[10:-1])

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
