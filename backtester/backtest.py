#!/usr/bin/python
# encoding: utf-8

#import ipdb as pdb
import sys
import os
import argparse
import json

import pylab as plt

sys.path.append(str(os.environ['QTRADE']))
from pyTrade.compute.Engine import Simulation

#from zipline.data.benchmarks import *


if __name__ == '__main__':
    ''' ----------------------------------------------------------------------------    Parsing Configuration    ----'''
    #TODO: the module allows many improvements
    parser = argparse.ArgumentParser(description='Backtester module, the terrific financial simukation')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s v0.8.1 Licence rien du tout', help='Print program version')
    parser.add_argument('-d', '--delta', type=int, action='store', default=1, required=False, help='Delta in days betweend two quotes fetch')
    parser.add_argument('-a', '--algorithm', action='store', required=True, help='Trading algorithm to be used')
    parser.add_argument('-m', '--manager', action='store', required=True, help='Portfolio strategie to be used')
    parser.add_argument('-b', '--database', action='store', default='stocks.db', required=False, help='Database location')
    parser.add_argument('-l', '--level', action='store', default='debug', required=False, help='Verbosity level')
    parser.add_argument('-t', '--tickers', action='store', required=True, help='target names to process')
    parser.add_argument('-s', '--start', action='store', default='1/1/2006', required=False, help='Start date of the backtester')
    parser.add_argument('-e', '--end', action='store', default='1/12/2010', required=False, help='Stop date of the backtester')
    parser.add_argument('-i', '--interactive', action='store_true', help='Indicates if the program was ran manually or not')
    args = parser.parse_args()

    if args.interactive:
        algo_config = json.load(open('algos.cfg', 'r'))[args.algorithm]
        manager_config = json.load(open('managers.cfg', 'r'))[args.manager]
    else:
        algo_config_str = raw_input('algo > ')
        manager_config_str = raw_input('manager > ')
        try:
            algo_config = json.loads(algo_config_str)
            manager_config = json.loads(manager_config_str)
        except:
            print('** Error loading json configuration.')
            sys.exit(1)

    '''-------------------------------------------------------------------------------------------    Backtest    ----'''
    engine = Simulation(access=['database'], db_name=args.database, lvl=args.level)
    results = engine.runBacktest(args, algo_config, manager_config)

    '''---------------------------------------------------------------------------------------------    Results   ----'''
    engine._log.info('Last day result returns: {}'.format(results.returns[-1]))
    engine._log.info('Portfolio returns: {}'.format(results.portfolio_value[-1]))
    #NOTE Benchmark returns, see zipline/data/benchmark.py (s&p500, implement others and change to parametric calls)

    #TODO implement in datafeed a generic save method which call the correct database save method
    #NOTE Could do a generic save client method (retrieve the correct model, with correct fields)
    perf_series  = engine.rolling_performances(timestamp='one_month', save=True, db_id='test')
    #returns_df   = engine.get_returns(freq=pd.datetools.BDay(), benchmark=True, save=True, db_id='pouet')
    risk_metrics = engine.overall_metrics(save=True, db_id='test')

    if args.interactive:
        engine._log.info('\n\nReturns: {}% / {}%\nVolatility:\t{}\nSharpe:\t\t{}\nMax drawdown:\t{}\n\n'.format(
            risk_metrics['Returns'] * 100.0, risk_metrics['Benchmark.Returns'] * 100.0, risk_metrics['Volatility'],
            risk_metrics['Sharpe.Ratio'], risk_metrics['Max.Drawdown']))
        os.system('./analysis.R')
        os.system('evince Rplots.pdf')

        results.portfolio_value.plot()
        results.returns.plot()
        plt.show()


''' Notes
Strategies to swich strategies =)
Backtest the strategy on many datasets, and check correlations to test algorithm efficiecy
'''
''' Backtest stocks selection
1.  a. Choose m stocks according to their best momentum or sharpe ratio for example
    b. Select n stocks from m according to portfolio optimization
'''
''' Backtest results analysis
1. Comparison with market benchmark (relative plot and values)
2. Comparison with buyAndHold, Mean-reversion, Trend-following algorithm (Multiple Backtest at a time)
3. Treynor ratio = mean(R(portfolio)) / beta(portfolio)
4. Sharpe ratio
5. Jensen measure (alpha (or excess returns or both here))
6. The maximum of max drawdown
7. Of course the portfolio final return and value
8. Value at Risk
9. Everything from coursera about returns distribution(max, min, mean, variance, kurtosis, skewness)
'''
