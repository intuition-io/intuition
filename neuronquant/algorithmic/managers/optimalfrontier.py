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


import os

import pandas as pd
import rpy2.robjects as robjects

from portfolio import PortfolioManager


class OptimalFrontier(PortfolioManager):
    '''
    Compute with R the efficient frontier and pick up the optimize point on it
    '''
    def __init__(self, parameters):
        PortfolioManager.__init__(self, parameters)

        # R stuff: R functions file and rpy interface
        self.r = robjects.r
        portfolio_opt_file = '/'.join((os.environ['QTRADE'], 'neuronquant/algorithmic/managers/opt_utils.R'))
        self.r('source("{}")'.format(portfolio_opt_file))

    def optimize(self, date, to_buy, to_sell, parameters):
        symbols     = []
        allocations = dict()

        # Considere only portfolio positions + future positions - positions about to be sold
        positions = set([t for t in self.portfolio.positions.keys() if self.portfolio.positions[t].amount]).union(to_buy).difference(to_sell)
        if not positions and to_sell:
            for t in to_sell:
                allocations[t] = - parameters.get('perc_sell', 1.0)
            return allocations, 0, 1
        try:
            assert(positions)
        except:
            self.log.error('** No positions determined')
        if len(positions) == 1:
            return {positions.pop(): parameters.get('max_weigths', 0.2)}, 0, 1
        for p in positions:
            symbols.append(self.datafeed.guess_name(p).lower())

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
