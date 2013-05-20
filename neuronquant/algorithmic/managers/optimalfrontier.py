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
import re

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
        portfolio_opt_file = '/'.join((os.environ['QTRADE'],
            'neuronquant/algorithmic/managers/opt_utils.R'))
        self.r('source("{}")'.format(portfolio_opt_file))

    def optimize(self, date, to_buy, to_sell, parameters):
        allocations = dict()

        # Considere only portfolio positions + future positions - positions about to be sold
        positions = set([t for t in self.portfolio.positions.keys()
                         if self.portfolio.positions[t].amount]).union(to_buy).difference(to_sell)
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

        if 'historical_prices' in parameters['algo']:
            #TODO The converion needs dates, should get the complete dataframe
            raise NotImplementedError()
            returns = pd.rpy.common.convert_to_r_matrix(pd.DataFrame(parameters['algo']['historical_prices']))
        else:
            returns = self.remote.fetch_equities_daily(
                positions, r_type=True, returns=True, indexes={},
                start=date-pd.datetools.Day(parameters.get('loopback', 50)),
                end=date)

        frontier = self.r('getEfficientFrontier')(returns,
            points=500, Debug=False, graph=False)
        if not frontier:
            self.log.warning('No optimal frontier found')
            return dict(), None, None

        try:
            mp = self.r('marketPortfolio')(frontier, 0.02, Debug=False, graph=False)
        except:
            self.log.error('** Error running R optimizer')
            return dict(), None, None

        self.log.debug('Allocation: {}'.format(mp))
        #FIXME Some key errors survive so far
        for p in positions:
            #NOTE R change a bit names
            try:
                allocations[p] = round(mp.rx(re.sub("[-,!\ ]", ".", p))[0][0], 2)
            except:
                import ipdb; ipdb.set_trace()

        er   = round(mp.rx('er')[0][0], 2)
        eStd = round(mp.rx('eStd')[0][0], 2)
        self.log.info('Allocation: {} With expected return: {} and expected risk: {}'.format(allocations, er, eStd))

        return allocations, er, eStd


''' Zipline notes:
self.portfolio.cash + self.portfolio.positions_value = self.portfolio.portfolio_value
self.portfolio.capital_used = self.portfolio.starting_cash - self.portfolio.cash

ipdb> self.portfolio.positions
{'Air Products and ': Position({'amount': 100, 'last_sale_price': 47.5, 'cost_basis': 47.5775, 'sid': 'Air Products and '})}

The manager could monitor many stuff: winning trades, positions, frequency...
'''
