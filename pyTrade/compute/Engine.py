from Algorithms import *

import ipdb as pdb
import sys
import os

sys.path.append(str(os.environ['QTRADE']))
from pyTrade.data.datafeed import DataFeed
#from pyTrade.data.DataAgent import DataAgent
from pyTrade.utils.LogSubsystem import LogSubsystem
from pyTrade.ai.manager import equity, optimal_frontier

import pytz
import pandas as pd
import numpy as np

from qstkutil import tsutil as tsu

#from zipline.data.benchmarks import *


class BacktesterEngine(object):
    ''' Factory class wrapping zipline Backtester, returns the requested algo '''
    algos = {'DualMA'      : DualMovingAverage       , 'Momentum'   : Momentum,
             'VWAP'        : VolumeWeightAveragePrice, 'BuyAndHold' : BuyAndHold,
             'StddevBased' : StddevBased             , 'OLMAR'      : OLMAR}

    portfolio_strategie = {'Equity': equity, 'OptimalFrontier': optimal_frontier}

    def __new__(self, algo, manager, algo_params, pf_params):
        if algo not in BacktesterEngine.algos:
            raise NotImplementedError('Algorithm {} not available or implemented'.format(algo))
        print('[Debug] Algorithm {} available, getting a reference to it.'.format(algo))
        if manager not in BacktesterEngine.portfolio_strategie:
            raise NotImplementedError('Manager {} not available or implemented'.format(manager))
        print('[Debug] Manager {} available, getting a reference to it.'.format(manager))
        return BacktesterEngine.algos[algo](algo_params, BacktesterEngine.portfolio_strategie[manager], pf_params)


class Simulation(object):
    ''' Take a trading strategie and evalute its results '''
    def __init__(self, access=['database', 'csv'], db_name='stocks.db', lvl='debug'):
        self._log = LogSubsystem('Simulation', lvl).getLog()
        self.feeds = DataFeed()
        #self.agent = DataAgent()
        #self.agent.connectTo(access, db_name=db_name, lvl=lvl)

    def runBacktest(self, args, algo_params, portfolio_params=None):
        #NOTE Do not like much to have to split here tickers
        #TODO Implement portfolio stragegy selection
        '''--------------------------------------------    Parameters    -----'''
        tickers = args.tickers.split(',')
        if isinstance(args.start, str) and isinstance(args.end, str):
            start = pytz.utc.localize(pd.datetime.strptime(args.start, '%Y-%m-%d'))
            end = pytz.utc.localize(pd.datetime.strptime(args.end, '%Y-%m-%d'))
        elif isinstance(args.start, dt.datetime) and isinstance(args.end, dt.datetime):
            raise NotImplementedError()
        else:
            raise NotImplementedError()
        if tickers[0] == 'random':
            assert(len(tickers) == 2)
            assert(int(tickers[1]))
            tickers = self.feeds.random_stocks(int(tickers[1]))

        data = self.feeds.quotes(tickers, start_date=args.start, end_date=args.end)
        if not data.index.tzinfo:
            self._log.warning('No timezone information')
            data.index = data.index.tz_localize(pytz.utc)
        assert isinstance(data, pd.DataFrame)
        assert data.index.tzinfo
        self.algorithm = args.algorithm

        '''-----------------------------------------------    Running    -----'''
        self._log.info('\n-- Running backetester, algorithm: {}\n'.format(args.algorithm))
        self._log.info('\n-- Using portfolio manager: {}\n'.format(args.manager))
        strategie = BacktesterEngine(args.algorithm, args.manager, algo_params, portfolio_params)
        self.results, self.monthly_perfs = strategie.run(data, start, end)
        return self.results

    def rolling_performances(self, timestamp='one_month', save=False, db_id=None):
        ''' Filters self.perfs and, if asked, save it to database '''
        #TODO Study the impact of month choice
        #TODO Check timestamp in an enumeration
        perfs = dict()
        length = range(len(self.monthly_perfs[timestamp]))
        index = self._get_index(self.monthly_perfs[timestamp])

        if db_id is None:
            db_id = self.algorithm + pd.datetime.strftime(pd.datetime.now(), format='%Y%m%d')
        perfs['Name']                 = np.array([db_id] * len(self.monthly_perfs[timestamp]))
        #perfs['Period']               = np.array([self.monthly_perfs[timestamp][i]['period_label'] for i in length])
        perfs['Period']               = np.array([pd.datetime.date(date) for date in index])
        perfs['Sharpe.Ratio']         = np.array([self.monthly_perfs[timestamp][i]['sharpe'] for i in length])
        perfs['Returns']              = np.array([self.monthly_perfs[timestamp][i]['algorithm_period_return'] for i in length])
        perfs['Max.Drawdown']         = np.array([self.monthly_perfs[timestamp][i]['max_drawdown'] for i in length])
        perfs['Volatility']           = np.array([self.monthly_perfs[timestamp][i]['algo_volatility'] for i in length])
        perfs['Beta']                 = np.array([self.monthly_perfs[timestamp][i]['beta'] for i in length])
        perfs['Alpha']                = np.array([self.monthly_perfs[timestamp][i]['alpha'] for i in length])
        perfs['Excess.Returns']       = np.array([self.monthly_perfs[timestamp][i]['excess_return'] for i in length])
        perfs['Benchmark.Returns']    = np.array([self.monthly_perfs[timestamp][i]['benchmark_period_return'] for i in length])
        perfs['Benchmark.Volatility'] = np.array([self.monthly_perfs[timestamp][i]['benchmark_volatility'] for i in length])
        perfs['Treasury.Returns']     = np.array([self.monthly_perfs[timestamp][i]['treasury_period_return'] for i in length])

        data = pd.DataFrame(perfs, index=index)

        if save:
            self.feeds.stock_db.save_metrics(data)
        return data

    def overall_metrics(self, timestamp='one_month', save=False, db_id=None):
        ''' Use zipline results to compute some performance indicators and store it in database '''
        perfs = dict()
        try:
            metrics = self.rolling_performances(timestamp=timestamp, save=False, db_id=db_id)
            riskfree = np.mean(metrics['Treasury.Returns'])

            if db_id is None:
                db_id = self.algorithm + pd.datetime.strftime(pd.datetime.now(), format='%Y%m%d')
            perfs['Name']              = db_id
            perfs['Sharpe.Ratio']      = tsu.get_sharpe_ratio(metrics['Returns'].values, risk_free = riskfree)
            perfs['Returns']           = (((metrics['Returns'] + 1).cumprod()) - 1)[-1]
            perfs['Max.Drawdown']      = min(metrics['Max.Drawdown'])
            perfs['Volatility']        = np.mean(metrics['Volatility'])
            perfs['Beta']              = np.mean(metrics['Beta'])
            perfs['Alpha']             = np.mean(metrics['Alpha'])
            perfs['Benchmark.Returns'] = (((metrics['Benchmark.Returns'] + 1).cumprod()) - 1)[-1]
        except:
            pdb.set_trace()

        if save:
            self.feeds.stock_db.save_performances(perfs)
        return perfs

    #TODO Rewrite
    def get_returns(self, freq=pd.datetools.BDay(), benchmark=False, timestamp='one_month', save=False, db_id=None):
        df = pd.DataFrame()
        returns = dict()

        returns['Benchmark.Returns']  = self._extract_perf(self.monthly_perfs[timestamp], 'benchmark_period_return')
        returns['Benchmark.CReturns'] = ((perfs['Benchmark.Returns'] + 1).cumprod()) - 1
        returns['Returns']            = self._extract_perf(self.monthly_perfs[timestamp], 'algorithm_period_return')
        returns['CReturns']           = ((perfs['algo_rets'] + 1).cumprod()) - 1

        df = pd.DataFrame(perfs, index=perfs['Returns'].index)

        if save:
            self.feeds.saveDFToDB(df, table_name=db_id)
        return df

    def _get_index(self, perfs):
        #NOTE No frequency infos or just period number ?
        start = pytz.utc.localize(pd.datetime.strptime(perfs[0]['period_label'] + '-01', '%Y-%m-%d'))
        end = pytz.utc.localize(pd.datetime.strptime(perfs[-1]['period_label'] + '-01', '%Y-%m-%d'))
        return pd.date_range(start - pd.datetools.BDay(10), end, freq=pd.datetools.BMonthBegin())

    def _extract_perf(self, perfs, field):
        index = self._get_index(perfs)
        values = [perfs[i][field] for i in range(len(perfs))]
        return pd.Series(values, index=index)
