#!/usr/bin/python

import ipdb as pdb

import sys
import os
import argparse
import json

import matplotlib.pyplot as plt

sys.path.append(str(os.environ['QTRADE']))
from pyTrade.data.DataAgent import DataAgent
from pyTrade.compute.Algorithms import BacktesterEngine
from pyTrade.utils.LogSubsystem import LogSubsystem

import datetime as dt
import pytz
import pandas as pd
import pandas.io.sql as pd_sql

from zipline.data.benchmarks import *


class Simulation(object):
    ''' Take a trading strategie and evalute its results '''
    def __init__(self, access=['database', 'csv'], db_name='stocks.db', logger=None, lvl='debug'):
        if not logger:
            self._log = LogSubsystem('Simulation', lvl).getLog()
        else:
            self._log = logger
        self.agent = DataAgent()
        self.agent.connectTo(access, db_name=db_name, lvl=lvl)
        pass

    def runBacktest(self, args, algo_params, price='actual_close'):
        #TODO This parameters make the class generic
        '''--------------------------------------------    Parameters    -----'''
        self.trading_algo = args.algorithm
        if isinstance(args.start, str) and isinstance(args.end, str):
            start = pytz.utc.localize(pd.datetime.strptime(args.start, '%d/%m/%Y'))
            end = pytz.utc.localize(pd.datetime.strptime(args.end, '%d/%m/%Y'))
        elif isinstance(args.start, dt.datetime) and isinstance(args.end, dt.datetime):
            raise NotImplementedError()
        else:
            raise NotImplementedError()
        self.timestamp = pd.date_range(start, end, freq=pd.datetools.BDay(args.delta))

        #data_all = agent.getQuotes(args.tickers.split(','), ['adj_close'], index=timestamp, reverse=True)
        data_all = self.agent.load_from_csv(args.tickers.split(','), fields=[price],
                                            index=self.timestamp, reverse=True)
        data = data_all[price]
        if not data.index.tzinfo:
            self._log.warning('No timezone information')
            data.index = data.index.tz_localize(pytz.utc)
        assert isinstance(data, pd.DataFrame)
        assert data.index.tzinfo

        '''-----------------------------------------------    Running    -----'''
        self._log.info('\n-- Running backetester, algorithm: {}\n'.format(args.algorithm))
        strategie = BacktesterEngine(args.algorithm, algo_params)
        self.results = strategie.run(data, start, end)
        self.monthly_perfs = strategie.cum_perfs[0]
        return strategie, self.results

    def filterPerfs(self, cum_perfs):
        ''' Take a cum_perfs zipline object and only keep
        interesting fields, easier to compute ahead'''
        pass

    def evaluateBacktest(self, timestamp='one_month', table_name=None, save=False):
        #TODO Study the impact of month choice
        #TODO Check timestamp in an enumeration
        table = None
        df = pd.DataFrame()
        graph = dict()

        graph['bench_rets'] = self._extract_perf(self.monthly_perfs[timestamp], 'benchmark_period_return')
        graph['bench_cum_rets'] = ((graph['bench_rets'] + 1).cumprod()) - 1

        graph['algo_rets'] = self._extract_perf(self.monthly_perfs[timestamp], 'algorithm_period_return')
        graph['algo_cum_rets'] = ((graph['algo_rets'] + 1).cumprod()) - 1

        graph['max_drawdown'] = - self._extract_perf(self.monthly_perfs[timestamp], 'max_drawdown')

        #NOTE Don't know why index has to be added
        df = pd.DataFrame(graph, index=graph['algo_rets'].index)

        if save:
            table = self.saveDFToDB(df, table_name=table_name)
        return df, table

    def _get_index(self, perfs):
        #NOTE No frequency infos or just period number ?
        start = pytz.utc.localize(pd.datetime.strptime(perfs[0]['period_label'] + '-30', '%Y-%m-%d'))
        end = pytz.utc.localize(pd.datetime.strptime(perfs[-1]['period_label'] + '-30', '%Y-%m-%d'))
        return pd.date_range(start, end, freq=pd.datetools.BMonthEnd())

    def _extract_perf(self, perfs, field):
        index = self._get_index(perfs)
        values = [perfs[i][field] for i in range(len(perfs) - 1)]
        return pd.Series(values, index=index)

    #TODO Move everything toward QuantDB
    def fromCSVtoSQL(self, csv_file):
        data = pd.read_table(csv_file)
        self.saveDFToDB(data)

    def readDFFromDB(self, table_name, limit=None):
        if not limit:
            df = pd_sql.read_frame('select * from %s' % table_name, self.agent.db._connection)
        else:
            df = pd_sql.read_frame('select * from %s limit %s' % (table_name, limit), self.agent.db._connection)
        try:
            df.index = pd.DatetimeIndex(df['date'])
            df.pop('date')
        except:
            self._log.error('** Creating dataframe index from sqlite read')
        return df

    def saveDFToDB(self, results, table_name=None):
        #TODO Temporary, will be move to QuantDB
        #NOTE Always drop ?
        if not table_name:
            table_name = '_'.join((self.trading_algo, dt.datetime.strftime(dt.datetime.now(), format='%d%m%Y')))
        self._log.info('Dropping previous table')
        self.agent.db.execute('drop table if exists %s' % table_name)
        self._log.info('Saving results (id:{})'.format(self.monthly_perfs['created']))
        results['date'] = results.index
        try:
            pd_sql.write_frame(results, table_name, self.agent.db._connection)
            self.agent.db.commit()
        except:
            pdb.set_trace()
        return table_name


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
    args = parser.parse_args()

    '''---------------------------------------------------------------------------------------'''
    '''
    2 solutions
        - From command line + json configuration file
        - From python server, command args as dict, others as json string
    '''
    config_str = raw_input()
    try:
        config = json.loads(config_str)
        print('Config: {}'.format(config_str))
    except:
        print('** Error loading json configuration.')
    params = {'short_window': 200, 'long_window': 400,
              'buy_on_event': 120, 'sell_on_event': 80}

    engine = Simulation(access=['database'], db_name=args.database, lvl=args.level)
    strategie, results = engine.runBacktest(args, config)
    '''---------------------------------------------------------------------------------------'''

    print('-----------------------------------------------------------------    Results   ----')
    engine._log.info('Last day result returns: {}'.format(results.returns[-1]))
    engine._log.info('Portfolio returns: {}'.format(strategie.portfolio['returns']))
    # Benchmark returns, see zipline/data/benchmark.py (s&p500, implement others and change to parametric calls)
    #TODO Create the overall metric
    engine._log.info('Benchmark returns: {}'.format(strategie.cum_perfs[-1]['one_month'][-1]['benchmark_period_return']))
    #TODO Other ratios, see paper
    engine._log.info('Sharpe ratio: {}'.format(strategie.cum_perfs[-1]['one_month'][-1]['sharpe']))
    engine._log.info('Max drawdown: {}'.format(strategie.cum_perfs[-1]['one_month'][-1]['max_drawdown']))

    df, table = engine.evaluateBacktest(timestamp='one_month', table_name='test', save=True)
    test = engine.readDFFromDB(table)
    #pdb.set_trace()

    results.portfolio_value.plot()
    results.returns.plot()
    #data['short'] = strategie.short_mavgs
    #data['long'] = strategie.long_mavgs
    #data[['google', 'short', 'long']].plot()
    plt.legend(loc=0)
    plt.show()


''' Notes
Strategies to swich strategies =)
Backtest the strategy on many datasets, and check correlations to test algorithm efficiecy
What is pairs trading ?
'''
''' Backtest stocks selection
1.  a. Choose m stocks according to their best momentum or sharpe ratio for example
    b. Select n stocks from n according to portfolio optimization
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
