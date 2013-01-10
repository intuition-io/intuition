#!/usr/bin/python

import ipdb as pdb

import sys
import os
import argparse

import matplotlib.pyplot as plt

sys.path.append(str(os.environ['QTRADE']))
from pyTrade.data.DataAgent import DataAgent
from pyTrade.compute.Algorithms import Backtester
import pytz
import pandas as pd

from zipline.data.benchmarks import *


def runBacktest(args, **kwargs):
    '''--------------------------------------------    Parameters    -----'''
    short_window = kwargs.get('short_window', 50)
    long_window = kwargs.get('long_window', 100)
    buy_on_event = kwargs.get('buy_on_event', 100)
    sell_on_event = kwargs.get('sell_on_event', 100)
    #start = pd.datetime(2001, 1, 20, 0, 0, 0, 0, pytz.utc)
    #end = pd.datetime(2009, 12, 20, 0, 0, 0, 0, pytz.utc)
    start = pytz.utc.localize(pd.datetime.strptime(args.start, '%d/%m/%Y'))
    end = pytz.utc.localize(pd.datetime.strptime(args.end, '%d/%m/%Y'))
    timestamp = pd.date_range(start, end, freq=pd.datetools.BDay(args.delta))

    agent = DataAgent()
    agent.connectTo(['remote', 'database'], db_name=args.database, lvl=args.level)
    data_all = agent.getQuotes(args.tickers.split(','), ['adj_close'], index=timestamp, reverse=True)
    data = data_all['adj_close']
    if not data.index.tzinfo:
        print('No timezone information')
        data.index = data.index.tz_localize(pytz.utc)

    '''-----------------------------------------------    Running    -----'''
    print('\n-- Running backetester, algorithm: {}\n'.format(args.algorithm))
    strategie = Backtester(args.algorithm, short_window=short_window, long_window=long_window,
                           capital_base=5000, buy_on_event=buy_on_event, sell_on_event=sell_on_event)
    results = strategie.run(data, start, end)
    return strategie, results


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
    parser.add_argument('-s', '--start', action='store', default='1/1/2000', required=False, help='Start date of the backtester')
    parser.add_argument('-e', '--end', action='store', default='1/12/2010', required=False, help='Stop date of the backtester')
    args = parser.parse_args()

    '''---------------------------------------------------------------------------------------'''
    strategie, results = runBacktest(args, short_window=40, long_window=80,
                                     buy_on_event=120, sell_on_event=80)
    '''---------------------------------------------------------------------------------------'''

    print('-----------------------------------------------------------------    Results   ----')
    #TODO a vector of results with:
    # Total returns
    print('Portfolio returns: {}'.format(strategie.portfolio.returns))
    # Benchmark returns, see zipline/data/benchmark.py (s&p500, implement others and change to parametric calls)
    print('Benchmark returns: {}'.format(get_benchmark_returns()[-1]))
    # Alpha
    # Beta
    # Sharpe
    # Volatility
    # Max Drawdown

    results.portfolio_value.plot()
    results.returns.plot()
    #data['short'] = strategie.short_mavgs
    #data['long'] = strategie.long_mavgs
    #data[['google', 'short', 'long']].plot()
    plt.legend(loc=0)
    plt.show()
