import os
import sys

import pytz
import pandas as pd

import ipdb as pdb

app_path = str(os.environ['QTRADE'])
sys.path.append(app_path)
portfolio_opt_file = '/'.join((app_path, 'pyTrade/ai/opt_utils.R'))
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
    #TODO Here is one, method, split it and allows to load other
    #TODO logger
    def __init__(self, commission_cost=0, lvl='debug'):
        super(PortfolioManager, self).__init__()
        self.agent = DataAgent()
        self.agent.connectTo(['database'], db_name='stocks.db', lvl=lvl)
        self.portfolio = None
        self.commission_cost = commission_cost
        r('source("{}")'.format(portfolio_opt_file))

    def update(self, portfolio):
        self.portfolio = portfolio

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

        #pdb.set_trace()
        if positions:
            if len(positions) == 1:
                alloc = {iter(positions).next(): 1}
            else:
                alloc, e_ret, e_risk = self._optimize_weigths(positions)
        for ticker in alloc:
            if ticker in self.portfolio.positions:
                n = int(round((available_money * alloc[ticker]) / self.portfolio.positions[ticker].last_sale_price))
                orderBook[ticker] = n - self.portfolio.positions[ticker].amount
            else:
                orderBook[ticker] = int(round((available_money * alloc[ticker]) / signals[ticker]))
        return orderBook

    #TODO R download each time the whole series
    def _optimize_weigths(self, tickers, start=None, to=None):
        """ compute the weights of tgiven tickers to hold in the portfolio  """
        if to is None:
            to = pd.datetime.strftime(pd.datetime.now(pytz.utc), format='%Y-%m-%d')
        if start is None:
            if isinstance(to, str):
                to_dt = pd.datetime.strptime(to, '%Y-%m-%d')
            elif isinstance(to, pd.datetime):
                to_dt = to
            start = pd.datetime.strftime(to_dt - pd.datetools.BDay(60), format='%Y-%m-%d')
        syms_dict_tmp, _ = self.agent.db.getTickersCodes(tickers)
        syms = [symbol.lower() for symbol in syms_dict_tmp.values()]
        symbols = r('c("{}")'.format('", "'.join(syms)))
        names = r('c("{}.Return")'.format('.Return", "'.join(syms)))
        try:
            data = r('importSeries')(symbols, start, to)
            frontier = r('getEfficientFrontier')(data, names, points=500, Debug=False, graph=False)
            mp = r('marketPortfolio')(frontier, 0.02, Debug=False, graph=False)
            print('Allocation: {}'.format(mp))
        except:
            print('** Error running R optimizer')
            return dict(), None, None
        allocations = dict()
        for s, t in zip(symbols, tickers):
            allocations[t] = round(mp.rx('.'.join((s, 'Return')))[0][0], 2)
        er = round(mp.rx('er')[0][0], 2)
        eStd = round(mp.rx('eStd')[0][0], 2)
        return allocations, er, eStd


if __name__ == '__main__':
    manager = PortfolioManager()
    allocations = manager._optimize_weigths(['google', 'apple', 'starbucks'])
    print allocations
