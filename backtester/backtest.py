#!/usr/bin/python
# encoding: utf-8
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

import sys
import os

import pylab as plt

from neuronquant.gears.engine import Simulation
from neuronquant.utils import color_setup, remote_setup, log


if __name__ == '__main__':
    # use 'setup' configuration for logging
    with color_setup.applicationbound():
        '''-------------------------------------------------------------------------------------------    Backtest    ----'''
        # Backtest or live engine used
        engine  = Simulation()

        # Read local (.cfg files and command line args) or remote (ZMQ Messages) backtest, algorithm and manager configuration
        args    = engine.configure()

        # See neuronquant/calculus/engine.py or zipline for details on results dataframe
        results = engine.run_backtest()
        if results is None:
            log.warning('Backtest failed, exiting')
            sys.exit(1)

        '''---------------------------------------------------------------------------------------------    Results   ----'''
        log.info('Portfolio returns: {}'.format(results.portfolio_value[-1]))

        if args['live'] or results.portfolio_value[-1] == args['cash']:
            # Currently tests don't last more than 20min, analysis is not relevant, neither backtest without orders
            sys.exit(0)

        #TODO Implement in datafeed a generic save method (which could call the correct database save method)
        #NOTE Could do a generic save client method (retrieve the correct model, with correct fields)
        perf_series  = engine.rolling_performances(timestamp='one_month', save=True, db_id=args['database'])
        #TODO save returns not ready yet, don't try to save
        returns_df   = engine.get_returns(benchmark='^fchi', save=False)
        risk_metrics = engine.overall_metrics(metrics=perf_series, save=True, db_id=args['database'])

        #FIXME irrelevant results if no transactions were made
        log.info('\n\nReturns: {}% / {}%\nVolatility:\t{}\nSharpe:\t\t{}\nMax drawdown:\t{}\n\n'.format(
                 risk_metrics['Returns'] * 100.0,
                 risk_metrics['Benchmark.Returns'] * 100.0,
                 risk_metrics['Volatility'],
                 risk_metrics['Sharpe.Ratio'],
                 risk_metrics['Max.Drawdown']))

        # If we work in local, draw a quick summary plot
        if not args['remote']:
            data = returns_df.drop(['Returns', 'Benchmark.Returns'], axis=1)
            data.plot()
            plt.show()

            # R statistical analysis
            os.system('{}/backtester/analysis.R --source mysql --table {} --verbose'.format(os.environ['QTRADE'], args['database']))
            os.system('evince ./Rplots.pdf')


''' Notes
Strategies to swich strategies =)
Backtest the strategy on many datasets, and check correlations to test algorithm efficiecy
Cross validation

Manager hint
1.  a. Choose m stocks according to their best momentum or sharpe ratio for example
    b. Select n stocks from m according to portfolio optimization
'''
