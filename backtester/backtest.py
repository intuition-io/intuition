#!/usr/bin/python
# encoding: utf-8

import ipdb as pdb
import sys
import os
import argparse
import json

import pylab as plt

sys.path.append(os.environ['QTRADE'])
from pyTrade.compute.engine import Simulation
from pyTrade.utils import setup, log

#from zipline.data.benchmarks import *


if __name__ == '__main__':
    with setup.applicationbound():
        '''-------------------------------------------------------------------------------------------    Backtest    ----'''
        engine  = Simulation()
        args    = engine.read_config()
        results = engine.runBacktest()

        '''---------------------------------------------------------------------------------------------    Results   ----'''
        log.info('Last day result returns: {}'.format(results.returns[-1]))
        log.info('Portfolio returns: {}'.format(results.portfolio_value[-1]))
        #NOTE Benchmark returns, see zipline/data/benchmark.py (s&p500, implement others and change to parametric calls)

        #TODO implement in datafeed a generic save method which call the correct database save method
        #NOTE Could do a generic save client method (retrieve the correct model, with correct fields)
        perf_series  = engine.rolling_performances(timestamp='one_month', save=True, db_id='test')
        #returns_df   = engine.get_returns(freq=pd.datetools.BDay(), benchmark=True, save=True, db_id='pouet')
        risk_metrics = engine.overall_metrics(save=True, db_id='test')

        #FIXME Should be executed when ran from nodejs debugger
        if args['interactive']:
            log.info('\n\nReturns: {}% / {}%\nVolatility:\t{}\nSharpe:\t\t{}\nMax drawdown:\t{}\n\n'.format(
                     risk_metrics['Returns'] * 100.0, risk_metrics['Benchmark.Returns'] * 100.0, risk_metrics['Volatility'],
                     risk_metrics['Sharpe.Ratio'], risk_metrics['Max.Drawdown']))
            results.portfolio_value.plot()
            #results.returns.plot()
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
