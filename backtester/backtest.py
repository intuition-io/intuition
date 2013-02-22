#!/usr/bin/python
# encoding: utf-8

import sys
import os

import pylab as plt

sys.path.append(os.environ['QTRADE'])
from neuronquant.compute.engine import Simulation
from neuronquant.utils import setup, log


if __name__ == '__main__':
    with setup.applicationbound():
        '''-------------------------------------------------------------------------------------------    Backtest    ----'''
        engine  = Simulation()
        args    = engine.configure()
        results = engine.runBacktest()

        '''---------------------------------------------------------------------------------------------    Results   ----'''
        log.info('Last day result returns: {}'.format(results.returns[-1]))
        log.info('Portfolio returns: {}'.format(results.portfolio_value[-1]))

        if args['live']:
            sys.exit(0)

        #TODO implement in datafeed a generic save method which call the correct database save method
        #NOTE Could do a generic save client method (retrieve the correct model, with correct fields)
        #perf_series  = engine.rolling_performances(timestamp='one_month', save=True, db_id='test')
        returns_df   = engine.get_returns(benchmark='SP500', save=False)
        risk_metrics = engine.overall_metrics(save=True, db_id='test')

        #FIXME Should be executed when ran from nodejs debugger, which is non-interactive
        if args['interactive']:
            log.info('\n\nReturns: {}% / {}%\nVolatility:\t{}\nSharpe:\t\t{}\nMax drawdown:\t{}\n\n'.format(
                     risk_metrics['Returns'] * 100.0, risk_metrics['Benchmark.Returns'] * 100.0, risk_metrics['Volatility'],
                     risk_metrics['Sharpe.Ratio'], risk_metrics['Max.Drawdown']))
            data = returns_df.drop(['Returns', 'Benchmark.Returns'], axis=1)
            data.plot()
            plt.show()

            #os.system('{}/backtester/analysis.R'.format(os.environ['QTRADE']))
            #os.system('evince {}/backtester/Rplots.pdf'.format(os.environ['QTRADE']))


''' Notes
Strategies to swich strategies =)
Backtest the strategy on many datasets, and check correlations to test algorithm efficiecy
'''
''' Backtest stocks selection
1.  a. Choose m stocks according to their best momentum or sharpe ratio for example
    b. Select n stocks from m according to portfolio optimization
'''
