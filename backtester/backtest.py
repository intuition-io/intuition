#!/usr/bin/python
# encoding: utf-8

import sys
import os

import pylab as plt

sys.path.append(os.environ['QTRADE'])
from neuronquant.calculus.engine import Simulation
from neuronquant.utils import color_setup, remote_setup, log


if __name__ == '__main__':
    # use 'setup' configuration for logging
    #with color_setup.applicationbound():
    with remote_setup.applicationbound():
        '''-------------------------------------------------------------------------------------------    Backtest    ----'''
        # Backtest or live engine used
        engine  = Simulation()

        # Read local (.cfg files and command line args) or remote (ZMQ Messages) backtest, algorithm and manager configuration
        args    = engine.configure()

        # See neuronquant/calculus/engine.py or zipline for details on results dataframe
        results = engine.run_backtest()

        '''---------------------------------------------------------------------------------------------    Results   ----'''
        log.info('Portfolio returns: {}'.format(results.portfolio_value[-1]))

        if args['live'] or results.portfolio_value[-1] == 100000:
            # Currently tests don't last more than 20min, analysis is not relevant, neither backtest without orders
            sys.exit(0)

        #TODO Implement in datafeed a generic save method (which could call the correct database save method)
        #NOTE Could do a generic save client method (retrieve the correct model, with correct fields)
        perf_series  = engine.rolling_performances(timestamp='one_month', save=True, db_id='test')
        #TODO save returns not ready yet, don't try to save
        returns_df   = engine.get_returns(benchmark='SP500', save=False)
        risk_metrics = engine.overall_metrics(save=True, db_id='test')

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
            os.system('{}/backtester/analysis.R'.format(os.environ['QTRADE']))
            os.system('evince {}/backtester/Rplots.pdf'.format(os.environ['QTRADE']))


''' Notes
Strategies to swich strategies =)
Backtest the strategy on many datasets, and check correlations to test algorithm efficiecy
Cross validation

Manager hint
1.  a. Choose m stocks according to their best momentum or sharpe ratio for example
    b. Select n stocks from m according to portfolio optimization
'''
