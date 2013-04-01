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


from portfolio import PortfolioManager


class Constant(PortfolioManager):
    '''
    Buy and sell a constant defined amount
    '''
    def optimize(self, date, to_buy, to_sell, parameters):
        '''
        Specifies the portfolio's allocation strategy
        The user can use :
        self.portfolio    : zipline portfolio object
        self.max_assets   : maximum assets the portfolio can have at a time
        self.max_weigths  : maximum weigth for an asset can have in the portfolio
        _____________________________________________
        Parameters
            date: datetime.timestamp
                Date signals were emitted
            to_buy: list(...)
                Symbols to buy triggered by the strategie signals
            to_sell: list(...)
                Symbols to sell triggered by the strategie signals
            parameters: dict(...)
                Custom user parameters
        _____________________________________________
        Return:
            allocations: dict(...)
                Symbols with their -> weigths -> for buy: according the whole portfolio value   (must be floats)
                                              -> for sell: according total symbol position in portfolio
                                   -> amount: number of stocks to process (must be ints)
            e_ret: float
                Expected return
            e_risk: float
                Expected risk
        '''
        allocations = dict()
        # Process every stock the same way
        for s in to_buy:
            # Allocate defined amount to buy
            allocations[s] = parameters.get('buy_amount', 100)
        for s in to_sell:
            allocations[s] = - parameters.get('sell_amount', self.portfolio.positions[s].amount)

        # Defaults values
        e_ret = 0
        e_risk = 1
        return allocations, e_ret, e_risk
