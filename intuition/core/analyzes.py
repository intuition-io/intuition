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

from finance import qstk_get_sharpe_ratio

import logbook

from zipline.data.benchmarks import get_benchmark_returns


log = logbook.Logger('intuition.core.analyze')


#NOTE Methods names to review
class Analyze():
    ''' Handle backtest results and performances measurments '''
    def __init__(self, *args, **kwargs):
        # R analysis file only need portfolio returns
        self.returns = kwargs.pop('returns') if 'returns' in kwargs else None

        # Final risk measurments as returned by the backtester
        self.results = kwargs.pop('results') if 'results' in kwargs else None

        # Simulation rolling performance
        self.metrics = kwargs.pop('metrics') if 'metrics' in kwargs else None

        # You better should know what was simulation's parameters
        self.configuration = kwargs.pop('configuration') if 'configuration' in kwargs else None

    def rolling_performances(self, timestamp='one_month', save=False, db_id=None):
        ''' Filters self.perfs and, if asked, save it to database '''
        #TODO Study the impact of month choice
        #TODO Check timestamp in an enumeration
        #TODO Implement other benchmarks for perf computation (zipline issue, maybe expected)

        #NOTE Script args define default database table name (test), make it consistent
        if db_id is None:
            db_id = self.configuration['algorithm'] + pd.datetime.strftime(pd.datetime.now(), format='%Y%m%d')

        if self.metrics:
            #TODO New fields from zipline: information, sortino
            perfs  = dict()
            length = range(len(self.metrics[timestamp]))
            index  = self._get_index(self.metrics[timestamp])
            perfs['Name']                 = np.array([db_id] * len(self.metrics[timestamp]))
            #perfs['Period']               = np.array([self.metrics[timestamp][i]['period_label'] for i in length])
            perfs['Period']               = np.array([pd.datetime.date(date)                                for date in index])
            perfs['Sharpe.Ratio']         = np.array([self.metrics[timestamp][i]['sharpe']                  for i in length])
            perfs['Sortino.Ratio']        = np.array([self.metrics[timestamp][i]['sortino']                 for i in length])
            perfs['Information']          = np.array([self.metrics[timestamp][i]['information']             for i in length])
            perfs['Returns']              = np.array([self.metrics[timestamp][i]['algorithm_period_return'] for i in length])
            perfs['Max.Drawdown']         = np.array([self.metrics[timestamp][i]['max_drawdown']            for i in length])
            perfs['Volatility']           = np.array([self.metrics[timestamp][i]['algo_volatility']         for i in length])
            perfs['Beta']                 = np.array([self.metrics[timestamp][i]['beta']                    for i in length])
            perfs['Alpha']                = np.array([self.metrics[timestamp][i]['alpha']                   for i in length])
            perfs['Excess.Returns']       = np.array([self.metrics[timestamp][i]['excess_return']           for i in length])
            perfs['Benchmark.Returns']    = np.array([self.metrics[timestamp][i]['benchmark_period_return'] for i in length])
            perfs['Benchmark.Volatility'] = np.array([self.metrics[timestamp][i]['benchmark_volatility']    for i in length])
            perfs['Treasury.Returns']     = np.array([self.metrics[timestamp][i]['treasury_period_return']  for i in length])
        else:
            #TODO Get it from DB if it exists
            raise NotImplementedError()

        data = pd.DataFrame(perfs, index=index)

        return data

    def overall_metrics(self, timestamp='one_month', metrics=None, db_id=None):
        '''
        Use zipline results to compute some performance indicators
        '''
        perfs = dict()

        # If no rolling perfs provided, computes it
        if metrics is None:
            metrics = self.rolling_performances(timestamp=timestamp, save=False, db_id=db_id)
        riskfree = np.mean(metrics['Treasury.Returns'])

        #NOTE Script args define default database table name (test), make it consistent
        if db_id is None:
            db_id = self.configuration['algorithm'] + pd.datetime.strftime(pd.datetime.now(), format='%Y%m%d')
        perfs['Name']              = db_id
        perfs['Sharpe.Ratio']      = qstk_get_sharpe_ratio(metrics['Returns'].values, risk_free=riskfree)
        perfs['Returns']           = (((metrics['Returns'] + 1).cumprod()) - 1)[-1]
        perfs['Max.Drawdown']      = max(metrics['Max.Drawdown'])
        perfs['Volatility']        = np.mean(metrics['Volatility'])
        perfs['Beta']              = np.mean(metrics['Beta'])
        perfs['Alpha']             = np.mean(metrics['Alpha'])
        perfs['Benchmark.Returns'] = (((metrics['Benchmark.Returns'] + 1).cumprod()) - 1)[-1]

        return perfs

    #TODO Save returns
    def get_returns(self, benchmark=''):
        returns = dict()

        if benchmark:
            try:
                benchmark_data = (
                    get_benchmark_returns(benchmark,
                                          self.configuration['index'][0],
                                          self.configuration['index'][-1]))
            except:
                raise KeyError()
        else:
            #TODO Automatic detection given exchange market (on command line) ?
            raise NotImplementedError()

        #NOTE Could be more efficient. But len(benchmark_data.date) !=
        # len(self.results.returns.index). Maybe because of different markets
        dates = pd.DatetimeIndex([d.date for d in benchmark_data])

        returns['Benchmark.Returns'] = pd.Series(
            [d.returns for d in benchmark_data], index=dates)
        returns['Benchmark.CReturns'] = (
            (returns['Benchmark.Returns'] + 1).cumprod()) - 1
        returns['Returns'] = pd.Series(
            self.results.returns.values, index=dates)
        returns['CReturns'] = pd.Series(
            ((self.results.returns.values + 1).cumprod()) - 1, index=dates)

        df = pd.DataFrame(returns, index=dates)

        if benchmark is None:
            df = df.drop(['Benchmark.Returns', 'Benchmark.CReturns'], axis=1)
        return df

    def _get_index(self, perfs):
        #NOTE No frequency infos or just period number ?
        start = pytz.utc.localize(pd.datetime.strptime(perfs[0]['period_label'] + '-01', '%Y-%m-%d'))
        end   = pytz.utc.localize(pd.datetime.strptime(perfs[-1]['period_label'] + '-01', '%Y-%m-%d'))
        return pd.date_range(start - pd.datetools.BDay(10), end, freq=pd.datetools.MonthBegin())

    def _extract_perf(self, perfs, field):
        index = self._get_index(perfs)
        values = [perfs[i][field] for i in range(len(perfs))]
        return pd.Series(values, index=index)
