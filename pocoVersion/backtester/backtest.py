#!/usr/bin/python
# encoding: utf-8

#import ipdb as pdb
import sys
import os
import argparse
import json

sys.path.append(str(os.environ['QTRADE']))
from pyTrade.compute.Engine import Simulation

#from zipline.data.benchmarks import *


if __name__ == '__main__':
    ''' --------------------------------------------    Parsing command line args    --------'''
    #TODO: the module allows many improvements
    parser = argparse.ArgumentParser(description='Backtester module, the terrific financial simukation')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s v0.8.1 Licence rien du tout', help='Print program version')
    parser.add_argument('-d', '--delta', type=int, action='store', default=1, required=False, help='Delta in days betweend two quotes fetch')
    parser.add_argument('-a', '--algorithm', action='store', required=True, help='Trading algorithm to be used')
    parser.add_argument('-b', '--database', action='store', default='stocks.db', required=False, help='Database location')
    parser.add_argument('-l', '--level', action='store', default='debug', required=False, help='Verbosity level')
    parser.add_argument('-t', '--tickers', action='store', required=True, help='target names to process')
    parser.add_argument('-s', '--start', action='store', default='1/1/2006', required=False, help='Start date of the backtester')
    parser.add_argument('-e', '--end', action='store', default='1/12/2010', required=False, help='Stop date of the backtester')
    parser.add_argument('-m', '--manual', action='store', default=False, required=False, help='Indicates if the program was ran manually')
    args = parser.parse_args()

    if args.manual:
        #config_str = '{"short_window": 100, "long_window": 200, "buy_on_event": 120, "sell_on_event": 80}'
        config = json.load(open('algos.cfg', 'r'))[args.algorithm]
    else:
        config_str = raw_input('config > ')
        try:
            config = json.loads(config_str)
        except:
            print('** Error loading json configuration.')
            sys.exit(1)

    '''---------------------------------------------------------------------------------------------    Backtest    --'''
    engine = Simulation(access=['database'], db_name=args.database, lvl=args.level)
    results, perfs = engine.runBacktest(args, config)
    '''---------------------------------------------------------------------------------------------------------------'''

    '''---------------------------------------------------------------------------------------------    Results   ----'''
    engine._log.info('Last day result returns: {}'.format(results.returns[-1]))
    engine._log.info('Portfolio returns: {}'.format(results.portfolio_value[-1]))
    # Benchmark returns, see zipline/data/benchmark.py (s&p500, implement others and change to parametric calls)
    #TODO Create the overall metric
    engine._log.info('Benchmark returns: {}'.format(perfs['one_month'][-1]['benchmark_period_return']))
    #TODO Other ratios, see paper
    engine._log.info('Sharpe ratio: {}'.format(perfs['one_month'][-1]['sharpe']))
    engine._log.info('Max drawdown: {}'.format(perfs['one_month'][-1]['max_drawdown']))

    df, table = engine.evaluateBacktest(timestamp='one_month', table_name='test', save=True)
    #test = engine.agent.db.readDFFromDB(table)
    #engine.agent.db.commit()
    #os.system('./analysis.R')
    #os.system('evince Rplots.pdf')

    #results.portfolio_value.plot()
    #results.returns.plot()
    #plt.show()


''' Notes
Strategies to swich strategies =)
Backtest the strategy on many datasets, and check correlations to test algorithm efficiecy
What is pairs trading ?
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

Plot: R package suggest 3 charts: - Benchmark and strategie cummulative returns
                                  - *ly returns around 0
                                  - Drawdown
'''
