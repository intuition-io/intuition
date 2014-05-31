# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Intuition results analyzer
  --------------------------

  Wraps session results with convenient analyse methods

  :copyright (c) 2014 Xavier Bruhiere
  :license: Apache 2.0, see LICENSE for more details.
'''

import pytz
import pandas as pd
import numpy as np
import dna.logging
import dna.debug
import dna.utils
from zipline.data.benchmarks import get_benchmark_returns
from intuition.finance import qstk_get_sharpe_ratio

log = dna.logging.logger(__name__)


class Analyze():
    ''' Handle backtest results and performances measurments '''
    def __init__(self, params, results, metrics, benchmark='^GSPC'):
        # NOTE Temporary
        # Simulation parameters
        self.sim_params = params
        # Final risk measurments as returned by the backtester
        self.results = results
        # Simulation rolling performance
        self.metrics = metrics
        # Market where we traded
        self.benchmark = benchmark

    def build_report(self, timestamp='one_month', show=False):
        # Get daily, cumulative and not, returns of portfolio and benchmark
        # NOTE Temporary fix before intuition would be able to get benchmark
        # data on live trading
        try:
            bm_sym = self.benchmark
            returns_df = self.get_returns(benchmark=bm_sym)
            skip = False
        except:
            log.warn('unable to get benchmark data on live trading for now')
            skip = True

        orders = 0
        for order in self.results.orders:
            orders += len(order)

        final_value = self.results.portfolio_value[-1]
        report = {
            'portfolio': final_value,
            'gain': final_value - self.sim_params.capital_base,
            'orders': orders,
            'pnl_mean': self.results.pnl.mean(),
            'pnl_deviation': self.results.pnl.std(),
        }
        if not skip:
            report['portfolio_perfs'] = returns_df['algo_c_return'][-1] * 100.0
            report['benchmark_perfs'] = \
                returns_df['benchmark_c_return'][-1] * 100.0

        perfs = self.overall_metrics(timestamp)
        for k, v in perfs.iteritems():
            report[k] = v

        # Float values for humans
        for key, value in report.iteritems():
            report[key] = dna.utils.truncate(value, 3)

        # Infinite sharpe ration breaks a lot of tools using this report
        # It usually happens when no transaction were processed
        if np.isinf(report['sharpe']):
            report['sharpe'] = 0.0

        log.info('generated report', report=report)
        if show:
            print
            print(dna.debug.emphasis(report, align=True))
            print
        return report

    def _to_perf_array(self, timestamp, key, length):
        return np.array([self.metrics[timestamp][i][key] for i in length])

    def rolling_performances(self, timestamp='one_month'):
        ''' Filters self.perfs '''
        # TODO Study the impact of month choice
        # TODO Check timestamp in an enumeration
        # TODO Implement other benchmarks for perf computation
        # (zipline issue, maybe expected)

        if self.metrics:
            perfs = {}
            length = range(len(self.metrics[timestamp]))
            index = self._get_index(self.metrics[timestamp])
            perf_keys = self.metrics[timestamp][0].keys()
            perf_keys.pop(perf_keys.index('period_label'))

            perfs['period'] = np.array(
                [pd.datetime.date(date) for date in index])
            for key in perf_keys:
                perfs[key] = self._to_perf_array(timestamp, key, length)
        else:
            # TODO Get it from DB if it exists
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
            # TODO Automatic detection given exchange market ?
            raise NotImplementedError()

        # NOTE Could be more efficient. But len(benchmark_data.date) !=
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
        # NOTE No frequency infos or just period number ?
        start = pytz.utc.localize(pd.datetime.strptime(
            perfs[0]['period_label'] + '-01', '%Y-%m-%d'))
        end = pytz.utc.localize(pd.datetime.strptime(
            perfs[-1]['period_label'] + '-01', '%Y-%m-%d'))
        return pd.date_range(start - pd.datetools.BDay(10),
                             end,
                             freq=pd.datetools.MonthBegin())
