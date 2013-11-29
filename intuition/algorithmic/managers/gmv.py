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
import numpy as np
import pandas as pd


def compute_weigths(daily_returns):
    try:
        #create a covariance matrix
        covariance_matrix = np.cov(daily_returns, y=None, rowvar=1,
                                   bias=0, ddof=None)
        covariance_matrix = np.matrix(covariance_matrix)

        #calculate global minimum portfolio weights
        one_vector = np.matrix(np.ones(len(daily_returns))).transpose()
        one_row = np.matrix(np.ones(len(daily_returns)))
        covariance_matrix_inv = np.linalg.inv(covariance_matrix)
        numerator = np.dot(covariance_matrix_inv, one_vector)
        denominator = np.dot(np.dot(one_row, covariance_matrix_inv), one_vector)

        return numerator / denominator
    except:
        return np.zeros(len(daily_returns))


class GlobalMinimumVariance(PortfolioManager):

    '''
    Global minimum Variance Portfolio
    https://www.quantopian.com/posts/global-minimum-variance-portfolio?c=1
    '''

    def optimize(self, date, to_buy, to_sell, parameters):

        allocations = {}

        for sid in to_sell:
            allocations[sid] = - self.portfolio.positions[sid].amount

        if len(to_buy) > 0:
            if 'historical_prices' in parameters['algo']:
                returns = parameters['algo']['historical_prices']
            else:
                #TODO Download it or check in database
                #NOTE Download allows here only daily data, use google instead ?
                self.log.notice('No returns provided, downloading them')
                returns_df = self.remote.fetch_equities_daily(
                    to_buy, returns=True, indexes={},
                    start=date-pd.datetools.Day(parameters.get('loopback', 50)),
                    end=date)
                returns = returns_df.values

            weights = compute_weigths(returns.transpose())
            if np.isnan(weights).any() or not weights.any():
                self.log.warning('Could not compute weigths')
                allocations = {}
            else:
                for i, sid in enumerate(to_buy):
                    allocations[sid] = float(weights[i])

        # Defaults values
        e_ret = 0
        e_risk = 1
        return allocations, e_ret, e_risk
