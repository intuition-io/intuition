import os
import sys

import pytz
import pandas as pd

import ipdb as pdb

sys.path.append(str(os.environ['QTRADE']))
from pyTrade.data.DataAgent import DataAgent

import rpy2.robjects as robjects
r = robjects.r


class PortfolioManager(object):
    '''
    This class observes the trader universe and makes orders
    @param amount    : initial portfolio value
    @param positions : list holding active positions like ["google", "apple"]
    @param level     : verbose level
    '''
    #TODO logger
    def __init__(self, commission_cost=0, lvl='debug'):
        super(PortfolioManager, self).__init__()
        self.agent = DataAgent()
        self.agent.connectTo(['database'], db_name='stocks.db', lvl=lvl)
        self.portfolio = None

    def updatePortfolio(self, portfolio):
        self.portfolio = portfolio

    def trade_signal_handler(self, signal):
        '''
        Process buy and sell signals from backtester or live trader
        @param signal: dict holding stocks of interest, format like {"google": 567.89, "apple": -345.98}
                       If the value is negative -> sell signal, otherwize buy one
        @return: dict orderBook, like {"google": 34, "apple": -56}
        '''
        positions = []
        orderBook = dict()
        pdb.set_trace()
        for ticker in set(self.portfolio.positions.keys).intersection(signal.keys()):
            orderBook[ticker] = - self.portfolio.positions[ticker].amount
        positions = set(self.portfolio.positions.keys).symmetric_difference(signal.keys())

        alloc, e_ret, e_risk = self._optimize_weigths(positions)
        for ticker in alloc:
            n = (self.portfolio.portfolio_value * alloc[ticker]) / signal[ticker]
            if self.portfolio.positions[ticker]:
                orderBook[ticker] = n - self.portfolio.positions[ticker]
            else:
                orderBook[ticker] = n
        return orderBook

    def _optimize_weigths(self, tickers, start=None, to=None):
        """ compute the weights of tgiven tickers to hold in the portfolio  """
        r('source("opt_utils.R")')
        if to is None:
            to = pd.datetime.strftime(pd.datetime.now(pytz.utc), format='%Y-%m-%d')
        if start is None:
            if isinstance(to, str):
                to_dt = pd.datetime.strptime(to, '%Y-%m-%d')
            elif isinstance(to, pd.datetime):
                to_dt = to
            start = pd.datetime.strftime(to_dt - pd.datetools.BDay(60), format='%Y-%m-%d')
        syms_dict_tmp, _ = self.agent.db.getTickersCodes(tickers)
        syms_dict = [symbol.lower() for symbol in syms_dict_tmp]
        symbols = r('c("{}")'.format('", "'.join(syms_dict.values())))
        names = r('c("{}.Return")'.format('.Return", "'.join(syms_dict.values())))
        try:
            data = r('importSeries')(symbols, start, to)
            frontier = r('getEfficientFrontier')(data, names, points=500, Debug=True, graph=False)
            mp = r('marketPortfolio')(frontier, 0.02, Debug=True, graph=False)
        except:
            print('** Error running R optimizer')
        allocations = dict()
        for s in symbols:
            allocations[s] = round(mp.rx('.'.join((s, 'Return')))[0][0], 2)
        er = round(mp.rx('er')[0][0], 2)
        eStd = round(mp.rx('eStd')[0][0], 2)
        return allocations, er, eStd


if __name__ == '__main__':
    allocations = _optimize_weigths(['google', 'apple', 'starbucks'])
    print allocations
