from Algorithms import *

import ipdb as pdb
import sys
import os


sys.path.append(str(os.environ['QTRADE']))
from pyTrade.data.datafeed import DataFeed
from pyTrade.data.DataAgent import DataAgent
from pyTrade.utils.LogSubsystem import LogSubsystem

#import datetime as dt
import pytz
import pandas as pd

#from zipline.data.benchmarks import *


class BacktesterEngine(object):
    ''' Factory class wrapping zipline Backtester, returns the requested algo '''
    algos = {'DualMA': DualMovingAverage, 'Momentum': Momentum,
             'VWAP': VolumeWeightAveragePrice, 'BuyAndHold': BuyAndHold,
             'StddevBased': StddevBased, 'OLMAR': OLMAR}

    def __new__(self, algo, params):
        if algo not in BacktesterEngine.algos:
            raise NotImplementedError('Algorithm {} not available or implemented'.format(algo))
        print('[Debug] Algorithm {} available, getting a reference to it.'.format(algo))
        return BacktesterEngine.algos[algo](params)


class Simulation(object):
    ''' Take a trading strategie and evalute its results '''
    def __init__(self, access=['database', 'csv'], db_name='stocks.db', lvl='debug'):
        self._log = LogSubsystem('Simulation', lvl).getLog()
        self.agent = DataAgent()
        self.agent.connectTo(access, db_name=db_name, lvl=lvl)
        pass

    def runBacktest(self, args, algo_params, price='actual_close'):
        #NOTE Do not like much to have to split here tickers
        #TODO Implement portfolio stragegy selection
        '''--------------------------------------------    Parameters    -----'''
        self.trading_algo = args.algorithm
        tickers = args.tickers.split(',')
        if isinstance(args.start, str) and isinstance(args.end, str):
            start = pytz.utc.localize(pd.datetime.strptime(args.start, '%Y-%m-%d'))
            end = pytz.utc.localize(pd.datetime.strptime(args.end, '%Y-%m-%d'))
        elif isinstance(args.start, dt.datetime) and isinstance(args.end, dt.datetime):
            raise NotImplementedError()
        else:
            raise NotImplementedError()
        feeds = DataFeed()
        if tickers[0] == 'random':
            assert(len(tickers) == 2)
            assert(int(tickers[1]))
            tickers = feeds.random_stocks(int(tickers[1]))
        data = feeds.quotes(tickers, start_date=args.start, end_date=args.end)

        #timestamp = pd.date_range(start, end, freq=pd.datetools.BDay(args.delta))
        #data_all = agent.getQuotes(args.tickers.split(','), ['adj_close'], index=timestamp, reverse=True)
        #data_all = self.agent.load_from_csv(args.tickers.split(','), fields=[price],
                                            #index=timestamp, reverse=True)
        #data = data_all[price]
        if not data.index.tzinfo:
            self._log.warning('No timezone information')
            data.index = data.index.tz_localize(pytz.utc)
        assert isinstance(data, pd.DataFrame)
        assert data.index.tzinfo

        '''-----------------------------------------------    Running    -----'''
        self._log.info('\n-- Running backetester, algorithm: {}\n'.format(args.algorithm))
        strategie = BacktesterEngine(args.algorithm, algo_params)
        self.results, self.monthly_perfs = strategie.run(data, start, end)
        return self.results, self.monthly_perfs

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
            table = self.agent.db.saveDFToDB(df, table_name=table_name)
        return df, table

    def _get_index(self, perfs):
        #NOTE No frequency infos or just period number ?
        start = pytz.utc.localize(pd.datetime.strptime(perfs[0]['period_label'] + '-01', '%Y-%m-%d'))
        end = pytz.utc.localize(pd.datetime.strptime(perfs[-1]['period_label'] + '-01', '%Y-%m-%d'))
        return pd.date_range(start - pd.datetools.BDay(10), end, freq=pd.datetools.BMonthBegin())

    def _extract_perf(self, perfs, field):
        index = self._get_index(perfs)
        values = [perfs[i][field] for i in range(len(perfs))]
        return pd.Series(values, index=index)
