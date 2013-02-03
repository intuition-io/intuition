import os
import sys

import pytz
import pandas as pd

from logbook import Logger

app_path = str(os.environ['QTRADE'])
sys.path.append(app_path)
portfolio_opt_file = '/'.join((app_path, 'pyTrade/ai/opt_utils.R'))
from pyTrade.data.datafeed import DataFeed

import rpy2.robjects as robjects
r = robjects.r


class PortfolioManager(object):
    '''
    This class observes the trader universe and makes orders
    @param amount    : initial portfolio value
    @param positions : list holding active positions like ["google", "apple"]
    @param level     : verbose level
    '''
    def __init__(self, commission_cost=0, lvl='debug'):
        super(PortfolioManager, self).__init__()
        self.log = Logger('Manager')
        self.feeds = DataFeed()
        self.portfolio = None
        self.date = None
        self.commission_cost = commission_cost
        r('source("{}")'.format(portfolio_opt_file))

    def update(self, portfolio, date):
        self.portfolio = portfolio
        self.date = date

    def trade_signals_handler(self, signals):
        '''
        Process buy and sell signals from backtester or live trader
        @param signals: dict holding stocks of interest, format like {"google": 567.89, "apple": -345.98}
                       If the value is negative -> sell signal, otherwize buy one
        @return: dict orderBook, like {"google": 34, "apple": -56}
        '''
        available_money = self.portfolio.portfolio_value
        orderBook = dict()
        alloc = dict()
        to_buy = [t for t in signals if signals[t] > 0]
        to_sell = set(self.portfolio.positions.keys()).intersection([t for t in signals if signals[t] < 0])
        for t in to_sell:
            orderBook[t] = - self.portfolio.positions[t].amount
            if self.portfolio.positions[t].amount > 250:
                available_money -= ((self.portfolio.positions[t].amount - 250) * abs(signals[t]))
        positions = set(self.portfolio.positions.keys()).union(to_buy).symmetric_difference(to_sell)

        if positions:
            if len(positions) == 1:
                alloc = {iter(positions).next(): 1}
            else:
                alloc, e_ret, e_risk = self._optimize_weigths(positions, self.date)
        for ticker in alloc:
            if ticker in self.portfolio.positions:
                n = int(round((available_money * alloc[ticker]) / self.portfolio.positions[ticker].last_sale_price))
                orderBook[ticker] = n - self.portfolio.positions[ticker].amount
            else:
                orderBook[ticker] = int(round((available_money * alloc[ticker]) / signals[ticker]))
        return orderBook

    def setup_strategie(self, callback, parameters):
        self._callback = callback
        self._optimizer_parameters = parameters

    def _optimize_weigths(self, positions, date):
        symbols = []
        pos_alloc = dict()
        for p in positions:
            symbols.append(DataFeed().guess_name(p).lower())
        syms_alloc, e_ret, e_risk = self._callback(symbols, date, self._optimizer_parameters)
        for s, t in zip(symbols, positions):
            pos_alloc[t] = syms_alloc[s]
        return pos_alloc, e_ret, e_risk


#NOTE A class for each, inhereted from manager that would override the strategie function ?
def equity(symbols, date, parameters):
    ''' Always allocate an equal part for each symbol '''
    allocations = dict()
    fraction = round(1.0 / float(len(symbols)), 2)
    for s in symbols:
        allocations[s] = fraction
    return allocations, 1, 0


def optimal_frontier(symbols, date, parameters):
    """ compute the weights of the given symbols to hold in the portfolio
        the R environment is set up, as well as inputs """
    allocations = dict()
    loopback = parameters.get('loopback', 50)
    source = parameters.get('source', 'yahoo')
    start = pd.datetime.strftime(date - pd.datetools.BDay(loopback), format='%Y-%m-%d')
    date = pd.datetime.strftime(date, format='%Y-%m-%d')
    r_symbols   = r('c("{}")'.format('", "'.join(symbols)))
    r_names     = r('c("{}.Return")'.format('.Return", "'.join(symbols)))
    try:
        data     = r('importSeries')(r_symbols, start, date, source=source)
        frontier = r('getEfficientFrontier')(data, r_names, points = 500, Debug   = False, graph = False)
        mp       = r('marketPortfolio')(frontier, 0.02, Debug      = False, graph = False)
        print('Allocation: {}'.format(mp))
    except:
        print('** Error running R optimizer')
        return dict(), None, None
    #FIXME Some key errors survive so far
    for s in symbols:
        allocations[s] = round(mp.rx('.'.join((s, 'Return')))[0][0], 2)
    er   = round(mp.rx('er')[0][0], 2)
    eStd = round(mp.rx('eStd')[0][0], 2)
    return allocations, er, eStd


if __name__ == '__main__':
    manager = PortfolioManager()
    manager.setup_strategie(equity)
    #manager.setup_strategie(optimal_frontier, lookback=60, source='mysql')
    allocations = manager._optimize_weigths(['google', 'apple', 'starbucks'], pd.datetime.now(pytz.utc))
    print allocations
