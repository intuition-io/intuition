import ipdb as pdb

import os
import sys

import pandas as pd
import rpy2.robjects as robjects

sys.path.append(os.environ['QTRADE'])
from pyTrade.data.datafeed import DataFeed
from pyTrade.ai.portfolio import PortfolioManager


class Constant(PortfolioManager):
    '''
    Simple buy and sell a constant defined amount
    '''
    def optimize(self, date, to_buy, to_sell, parameters):
        ''' This method has to be overwritten here
        @the user can use :
        self.portfolio    : zipline portfolio object
        self.max_assets   : maximum assets the portfolio can have at a time
        self.max_weigths  : maximum weigth for an asset can have in the portfolio
        @param to_buy     : symbols to buy according to the strategie signals
        @param to_sell    : symbols in the portfolio to sell according to the strategie signals
        @param date       : the date the signals were emitted
        @return a dictionnary of symbols with their -> weigths -> for buy: according the whole portfolio value   (must be floats)
                                                                  for sell: according total symbol position in portfolio
                                                    -> amount: number of stocks to process (must be ints)
                e_ret: expected return
                e_risk: expected risk
        '''
        allocations = dict()
        for s in to_buy:
            allocations[s] = parameters.get('buy_amount', 100)
        for s in to_sell:
            allocations[s] = - parameters.get('sell_amount', self.portfolio.positions[s].amount)
        e_ret = 0
        e_risk = 1
        return allocations, e_ret, e_risk


class Equity(PortfolioManager):
    '''
    dispatch equals weigths
    '''
    def optimize(self, date, to_buy, to_sell, parameters):
        allocations = dict()
        if to_buy:
            fraction = round(1.0 / float(len(to_buy)), 2)
            for s in to_buy:
                allocations[s] = fraction
        for s in to_sell:
            allocations[s] = - self.portfolio.positions[s].amount
        return allocations, 0, 1


class OptimalFrontier(PortfolioManager):
    '''
    Compute with R the efficient frontier and pick up the optimize point on it
    '''
    def __init__(self, parameters):
        PortfolioManager.__init__(self, parameters)
        self.feeds = DataFeed()
        portfolio_opt_file = '/'.join((os.environ['QTRADE'], 'pyTrade/ai/opt_utils.R'))
        self.r = robjects.r
        self.r('source("{}")'.format(portfolio_opt_file))

    def optimize(self, date, to_buy, to_sell, parameters):
        symbols     = []
        allocations = dict()

        positions = set(self.portfolio.positions.keys()).union(to_buy).difference(to_sell)
        if not positions and to_sell:
            for t in to_sell:
                allocations[t] = - parameters.get('perc_sell', 1.0)
            return allocations, 0, 1
        try:
            assert(positions)
        except:
            pdb.set_trace()
        if len(positions) == 1:
            return {positions.pop(): parameters.get('max_weigths', 0.2)}, 0, 1
        for p in positions:
            symbols.append(DataFeed().guess_name(p).lower())

        loopback    = parameters.get('loopback', 50)
        source      = parameters.get('source', 'yahoo')
        start       = pd.datetime.strftime(date - pd.datetools.BDay(loopback), format = '%Y-%m-%d')
        date        = pd.datetime.strftime(date, format = '%Y-%m-%d')
        r_symbols   = self.r('c("{}")'.format('", "'.join(symbols)))
        r_names     = self.r('c("{}.Return")'.format('.Return", "'.join(symbols)))
        data        = self.r('importSeries')(r_symbols, start, date, source=source)
        frontier = self.r('getEfficientFrontier')(data, r_names, points = 500, Debug   = False, graph = False)
        if not frontier:
            self.log.warning('No optimal frontier found')
            return dict(), None, None
        try:
            mp       = self.r('marketPortfolio')(frontier, 0.02, Debug      = False, graph = False)
        except:
            self.log.error('** Error running R optimizer')
            pdb.set_trace()
            return dict(), None, None
        self.log.debug('Allocation: {}'.format(mp))
        #FIXME Some key errors survive so far
        for s, t in zip(symbols, positions):
            allocations[t] = round(mp.rx('.'.join((s, 'Return')))[0][0], 2)
        er   = round(mp.rx('er')[0][0], 2)
        eStd = round(mp.rx('eStd')[0][0], 2)
        self.log.debug('Allocation: {}\nWith expected return: {}\tand expected risk: {}'.format(allocations, er, eStd))

        return allocations, er, eStd


''' Zipline notes:
self.portfolio.cash + self.portfolio.positions_value = self.portfolio.portfolio_value
self.portfolio.capital_used = self.portfolio.starting_cash - self.portfolio.cash

ipdb> self.portfolio.positions
{'Air Products and ': Position({'amount': 100, 'last_sale_price': 47.5, 'cost_basis': 47.5775, 'sid': 'Air Products and '})}

The manager could monitor many stuff: winning trades, positions, frequency...
'''
