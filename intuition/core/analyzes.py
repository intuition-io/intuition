#
# Copyright 2013 Xavier Bruhiere
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


import pytz
import pandas as pd
import numpy as np
import logbook

from zipline.data.benchmarks import get_benchmark_returns

from finance import qstk_get_sharpe_ratio


log = logbook.Logger('intuition.core.analyze')


class Analyze():
    ''' Handle backtest results and performances measurments '''
    def __init__(self, **kwargs):
        #FIXME Those None-values aren't check later
        # R analysis file only needs portfolio returns
        self.returns = kwargs.pop('returns') if 'returns' in kwargs else None

        # Final risk measurments as returned by the backtester
        self.results = kwargs.pop('results') if 'results' in kwargs else None

        # Simulation rolling performance
        self.metrics = kwargs.pop('metrics') if 'metrics' in kwargs else None

    def _to_perf_array(self, timestamp, key, length):
        return np.array([self.metrics[timestamp][i][key] for i in length])

    def rolling_performances(self, timestamp='one_month'):
        ''' Filters self.perfs '''
        #TODO Study the impact of month choice
        #TODO Check timestamp in an enumeration
        #TODO Implement other benchmarks for perf computation
        # (zipline issue, maybe expected)

        if self.metrics:
            perfs = {}
            length = range(len(self.metrics[timestamp]))
            index = self._get_index(self.metrics[timestamp])
            perf_keys = self.metrics['one_month'][0].keys()
            perf_keys.pop(perf_keys.index('period_label'))

            perfs['period'] = np.array(
                [pd.datetime.date(date) for date in index])
            for key in perf_keys:
                perfs[key] = self._to_perf_array(timestamp, key, length)
        else:
            #TODO Get it from DB if it exists
            raise NotImplementedError()

        return pd.DataFrame(perfs, index=index)

    def overall_metrics(self, timestamp='one_month', metrics=None):
        '''
        Use zipline results to compute some performance indicators
        '''
        perfs = dict()

        # If no rolling perfs provided, computes it
        if metrics is None:
            metrics = self.rolling_performances(timestamp=timestamp)
        riskfree = np.mean(metrics['treasury_period_return'])

        perfs['sharpe'] = qstk_get_sharpe_ratio(
            metrics['algorithm_period_return'].values, risk_free=riskfree)
        perfs['algorithm_period_return'] = (
            ((metrics['algorithm_period_return'] + 1).cumprod()) - 1)[-1]
        perfs['max_drawdown'] = max(metrics['max_drawdown'])
        perfs['algo_volatility'] = np.mean(metrics['algo_volatility'])
        perfs['beta'] = np.mean(metrics['beta'])
        perfs['alpha'] = np.mean(metrics['alpha'])
        perfs['benchmark_period_return'] = (
            ((metrics['benchmark_period_return'] + 1).cumprod()) - 1)[-1]

        return perfs

    def get_returns(self, benchmark=''):
        returns = {}

        if benchmark:
            try:
                benchmark_data = (
                    get_benchmark_returns(benchmark,
                                          self.results.index[0],
                                          self.results.index[-1]))
            except Exception as e:
                raise KeyError(e)
        else:
            #TODO Automatic detection given exchange market (on command line) ?
            raise NotImplementedError()

        #NOTE Could be more efficient. But len(benchmark_data.date) !=
        # len(self.results.returns.index). Maybe because of different markets
        dates = pd.DatetimeIndex([d.date for d in benchmark_data])

        returns['benchmark_return'] = pd.Series(
            [d.returns for d in benchmark_data], index=dates)
        returns['benchmark_c_return'] = (
            (returns['benchmark_return'] + 1).cumprod()) - 1
        returns['algo_return'] = pd.Series(
            self.results.returns.values, index=dates)
        returns['algo_c_return'] = pd.Series(
            ((self.results.returns.values + 1).cumprod()) - 1, index=dates)

        df = pd.DataFrame(returns, index=dates)

        if benchmark is None:
            df = df.drop(['benchmark_return', 'benchmark_c_return'], axis=1)
        return df

    def _get_index(self, perfs):
        #NOTE No frequency infos or just period number ?
        start = pytz.utc.localize(pd.datetime.strptime(
            perfs[0]['period_label'] + '-01', '%Y-%m-%d'))
        end = pytz.utc.localize(pd.datetime.strptime(
            perfs[-1]['period_label'] + '-01', '%Y-%m-%d'))
        return pd.date_range(start - pd.datetools.BDay(10),
                             end,
                             freq=pd.datetools.MonthBegin())
