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


from algorithms import *

import sys
import os
import argparse
import json

sys.path.append(os.environ['QTRADE'])
from neuronquant.data.datafeed import DataFeed
from neuronquant.ai.managers import Constant, Equity, OptimalFrontier
from neuronquant.network.transport import ZMQ_Dealer

import pytz
import pandas as pd
import numpy as np

from qstkutil import tsutil as tsu

import logbook
log = logbook.Logger('Engine')

from zipline.data.benchmarks import get_benchmark_returns


class BacktesterEngine(object):
    ''' Factory class wrapping zipline Backtester, returns the requested algo '''
    algos = {'DualMA'      : DualMovingAverage       , 'Momentum'   : Momentum,
             'VWAP'        : VolumeWeightAveragePrice, 'BuyAndHold' : BuyAndHold,
             'StdBased'    : StddevBased             , 'OLMAR'      : OLMAR,
             'MultiMA'     : MultiMA                 , 'MACrossover': MovingAverageCrossover}

    portfolio_strategie = {'Equity': Equity, 'Constant': Constant, 'OptimalFrontier': OptimalFrontier}

    def __new__(self, algo, manager, algo_params, pf_params):
        if algo not in BacktesterEngine.algos:
            raise NotImplementedError('Algorithm {} not available or implemented'.format(algo))
        log.info('[Debug] Algorithm {} available, getting a reference to it.'.format(algo))

        if manager not in BacktesterEngine.portfolio_strategie:
            raise NotImplementedError('Manager {} not available or implemented'.format(manager))
        log.info('[Debug] Manager {} available, getting a reference and initializing it.'.format(manager))

        #return BacktesterEngine.algos[algo](algo_params, BacktesterEngine.portfolio_strategie[manager](pf_params))
        #trading_algorithm = BacktesterEngine.algos[algo](algo_params, capital_base=100000)
        trading_algorithm = BacktesterEngine.algos[algo](algo_params)
        trading_algorithm.set_logger(Logger(algo))
        trading_algorithm.manager = BacktesterEngine.portfolio_strategie[manager](pf_params)

        return trading_algorithm


#NOTE engine.feed_data(tickers, start, end, freq) ?
class Simulation(object):
    ''' Take a trading strategie and evalute its results '''
    def __init__(self, data=None, flavor='mysql', lvl='debug'):
        #NOTE Allowing different data access ?
        self.data          = data
        if not data:
            self.feeds         = DataFeed()
        self.backtest_cfg  = None
        self.algo_cfg      = None
        self.manager_cfg   = None
        self.monthly_perfs = None

        self.server        = ZMQ_Dealer(id=self.__class__.__name__)

    def configure(self, bt_cfg=None, a_cfg=None, m_cfg=None):
        ''' Reads and provides a clean configuration for the simulation '''

        if not bt_cfg:
            parser = argparse.ArgumentParser(description='Backtester module, the terrific financial simukation')
            parser.add_argument('-v', '--version', action='version', version='%(prog)s v0.8.1 Licence rien du tout', help='Print program version')
            parser.add_argument('-d', '--delta', type=str, action='store', default='D', required=False, help='Delta in days betweend two quotes fetch')
            parser.add_argument('-a', '--algorithm', action='store', required=True, help='Trading algorithm to be used')
            parser.add_argument('-m', '--manager', action='store', required=True, help='Portfolio strategie to be used')
            parser.add_argument('-b', '--database', action='store', default='test', required=False, help='Table to considere in database')
            parser.add_argument('-t', '--tickers', action='store', required=True, help='target names to process')
            parser.add_argument('-s', '--start', action='store', default='1/1/2006', required=False, help='Start date of the backtester')
            parser.add_argument('-e', '--end', action='store', default='1/12/2010', required=False, help='Stop date of the backtester')
            parser.add_argument('-r', '--remote', action='store_true', help='Indicates if the program was ran manually or not')
            parser.add_argument('-l', '--live', action='store_true', help='makes the engine work in real-time !')
            parser.add_argument('-p', '--port', action='store', default=5570, required=False, help='Activates the diffusion of the universe on the network, on the port provided')
            args = parser.parse_args()

            self.backtest_cfg = {'algorithm'   : args.algorithm,
                                 'delta'       : args.delta,
                                 'manager'     : args.manager,
                                 'database'    : args.database,
                                 'tickers'     : args.tickers.split(','),
                                 'start'       : args.start,
                                 'end'         : args.end,
                                 'live'        : args.live,
                                 'port'        : args.port,
                                 'remote'      : args.remote}
        else:
            self.backtest_cfg = bt_cfg

        if isinstance(self.backtest_cfg['start'], str) and isinstance(self.backtest_cfg['end'], str):
            ###############test = pd.datetime.strptime('2012-02-01:14:00', '%Y-%m-%d:%H:%M')
            self.backtest_cfg['start'] = pytz.utc.localize(pd.datetime.strptime(self.backtest_cfg['start'], '%Y-%m-%d'))
            self.backtest_cfg['end']   = pytz.utc.localize(pd.datetime.strptime(self.backtest_cfg['end'], '%Y-%m-%d'))
        elif isinstance(self.backtest_cfg['start'], pd.datetime) and isinstance(self.backtest_cfg['end'], pd.datetime):
            if not self.backtest_cfg['start'].tzinfo:
                self.backtest_cfg['start'] = pytz.utc.localize(self.backtest_cfg['start'])
            if not self.backtest_cfg['end'].tzinfo:
                self.backtest_cfg['end'] = pytz.utc.localize(self.backtest_cfg['end'])
        else:
            raise NotImplementedError()

        #if self.backtest_cfg['interactive']:
        self.read_config(remote=self.backtest_cfg['remote'], manager=m_cfg, algorithm=a_cfg)
        #else:
            #self.server.run_forever(port=self.backtest_cfg['port'], on_recv=self.read_config)

        return self.backtest_cfg

    def read_config(self, *args, **kwargs):
        self.manager_cfg = kwargs.get('manager', None)
        self.algo_cfg = kwargs.get('algorithm', None)

        if kwargs.get('remote', False):
            self.server.run(host='127.0.0.1', port=self.backtest_cfg['port'])

            # In remote mode, client sends missing configuration through zmq socket
            if (not self.manager_cfg) or (not self.algo_cfg):
                log.info('Fetching backtest configuration from client')
                msg = self.server.receive(json=True)
                log.debug('Got it !')

            # Set simulation parameters with it
            assert isinstance(msg, dict)
            if self.manager_cfg is None:
                self.manager_cfg = msg['manager']
            if self.algo_cfg is None:
                self.algo_cfg    = msg['algorithm']

        else:
            # Reading configuration from json files
            config_dir = '/'.join((os.environ['QTRADE'], 'config/'))
            try:
                # Files store many algos and manager parameters,
                # use backtest configuration to pick up the right one
                if self.manager_cfg is None:
                    self.manager_cfg = json.load(open('{}/managers.cfg'.format(config_dir), 'r'))[self.backtest_cfg['manager']]
                if self.algo_cfg is None:
                    self.algo_cfg    = json.load(open('{}/algos.cfg'.format(config_dir), 'r'))[self.backtest_cfg['algorithm']]
            except:
                log.error('** loading json configuration.')
                sys.exit(1)

        # The manager can use the same socket during simulation to emit portfolio informations
        self.manager_cfg['server'] = self.server
        log.info('Configuration is Done.')

    def run_backtest(self):
        # No configuration, no backtest man
        if self.backtest_cfg is None or self.algo_cfg is None or self.manager_cfg is None:
            log.error('** Backtester not configured properly')
            return 1

        #'''_____________________________________________________________________    Parameters    ________
        if self.backtest_cfg['tickers'][0] == 'random':
            assert(len(self.backtest_cfg['tickers']) == 2)
            assert(int(self.backtest_cfg['tickers'][1]))
            self.backtest_cfg['tickers'] = self.feeds.random_stocks(int(self.backtest_cfg['tickers'][1]))

        if self.backtest_cfg['live']:
            #dates = pd.date_range(self.backtest_cfg['start'], self.backtest_cfg['end'], freq=self.backtest_cfg['delta'])
            #NOTE A temporary hack to avoid zipline dirty modification
            periods = self.backtest_cfg['end'] - self.backtest_cfg['start']
            dates = pd.date_range(pd.datetime.now(), periods=periods.days + 1, freq=self.backtest_cfg['delta'])
            '''
            if dates.freq > pd.datetools.Day():
                #fr_selector = ((dates.hour > 8) & (dates.hour < 17)) | ((dates.hour == 17) & (dates.minute < 31))
                us_selector = ((dates.hour > 15) & (dates.hour < 22)) | ((dates.hour == 15) & (dates.minute > 31))
                dates = dates[us_selector]
            if not dates:
                log.warning('! Market closed.')
                sys.exit(0)
            '''
            data = {'tickers': self.backtest_cfg['tickers'], 'index': dates.tz_localize(pytz.utc)}
        else:
            data = self.feeds.quotes(self.backtest_cfg['tickers'],
                                     start_date = self.backtest_cfg['start'],
                                     end_date   = self.backtest_cfg['end'])
            assert isinstance(data, pd.DataFrame)
            assert data.index.tzinfo

        #___________________________________________________________________________    Running    ________
        log.info('\n-- Running backetester...\nUsing algorithm: {}\n'.format(self.backtest_cfg['algorithm']))
        log.info('\n-- Using portfolio manager: {}\n'.format(self.backtest_cfg['manager']))

        backtester = BacktesterEngine(self.backtest_cfg['algorithm'],
                                      self.backtest_cfg['manager'],
                                      self.algo_cfg,
                                      self.manager_cfg)
        self.results, self.monthly_perfs = backtester.run(data)
                                                          #self.backtest_cfg['start'],
                                                          #self.backtest_cfg['end'])
        return self.results

    def rolling_performances(self, timestamp='one_month', save=False, db_id=None):
        ''' Filters self.perfs and, if asked, save it to database '''
        #TODO Study the impact of month choice
        #TODO Check timestamp in an enumeration

        #NOTE Script args define default database table name (test), make it consistent
        if db_id is None:
            db_id = self.backtest_cfg['algorithm'] + pd.datetime.strftime(pd.datetime.now(), format='%Y%m%d')

        if self.monthly_perfs:
            perfs  = dict()
            length = range(len(self.monthly_perfs[timestamp]))
            index  = self._get_index(self.monthly_perfs[timestamp])
            perfs['Name']                 = np.array([db_id] * len(self.monthly_perfs[timestamp]))
            #perfs['Period']               = np.array([self.monthly_perfs[timestamp][i]['period_label'] for i in length])
            perfs['Period']               = np.array([pd.datetime.date(date)                                      for date in index])
            perfs['Sharpe.Ratio']         = np.array([self.monthly_perfs[timestamp][i]['sharpe']                  for i in length])
            perfs['Returns']              = np.array([self.monthly_perfs[timestamp][i]['algorithm_period_return'] for i in length])
            perfs['Max.Drawdown']         = np.array([self.monthly_perfs[timestamp][i]['max_drawdown']            for i in length])
            perfs['Volatility']           = np.array([self.monthly_perfs[timestamp][i]['algo_volatility']         for i in length])
            perfs['Beta']                 = np.array([self.monthly_perfs[timestamp][i]['beta']                    for i in length])
            perfs['Alpha']                = np.array([self.monthly_perfs[timestamp][i]['alpha']                   for i in length])
            perfs['Excess.Returns']       = np.array([self.monthly_perfs[timestamp][i]['excess_return']           for i in length])
            perfs['Benchmark.Returns']    = np.array([self.monthly_perfs[timestamp][i]['benchmark_period_return'] for i in length])
            perfs['Benchmark.Volatility'] = np.array([self.monthly_perfs[timestamp][i]['benchmark_volatility']    for i in length])
            perfs['Treasury.Returns']     = np.array([self.monthly_perfs[timestamp][i]['treasury_period_return']  for i in length])
        else:
            #TODO Get it from DB if it exists
            raise NotImplementedError()

        try:
            data = pd.DataFrame(perfs, index=index)
        except:
            import ipdb; ipdb.set_trace()

        if save:
            self.feeds.stock_db.save_metrics(data)
        return data

    def overall_metrics(self, timestamp='one_month', save=False, db_id=None):
        ''' Use zipline results to compute some performance indicators and store it in database '''
        perfs = dict()
        metrics = self.rolling_performances(timestamp=timestamp, save=False, db_id=db_id)
        riskfree = np.mean(metrics['Treasury.Returns'])

        #NOTE Script args define default database table name (test), make it consistent
        if db_id is None:
            db_id = self.backtest_cfg['algorithm'] + pd.datetime.strftime(pd.datetime.now(), format='%Y%m%d')
        perfs['Name']              = db_id
        perfs['Sharpe.Ratio']      = tsu.get_sharpe_ratio(metrics['Returns'].values, risk_free = riskfree)
        perfs['Returns']           = (((metrics['Returns'] + 1).cumprod()) - 1)[-1]
        perfs['Max.Drawdown']      = max(metrics['Max.Drawdown'])
        perfs['Volatility']        = np.mean(metrics['Volatility'])
        perfs['Beta']              = np.mean(metrics['Beta'])
        perfs['Alpha']             = np.mean(metrics['Alpha'])
        perfs['Benchmark.Returns'] = (((metrics['Benchmark.Returns'] + 1).cumprod()) - 1)[-1]

        if save:
            self.feeds.stock_db.save_performances(perfs)
        return perfs

    #TODO Save returns
    def get_returns(self, benchmark=None, timestamp='one_month', save=False, db_id=None):
        returns = dict()

        if benchmark:
            #TODO Benchmark fields in database for guessing name like for stocks
            benchmark_symbol = '^GSPC'
            benchmark_data  = get_benchmark_returns(benchmark_symbol, self.backtest_cfg['start'], self.backtest_cfg['end'])
        else:
            raise NotImplementedError()
        #benchmark_data = [d for d in benchmark_data if (d.date >= self.backtest_cfg['start']) and (d.date <= self.backtest_cfg['end'])]
        dates = pd.DatetimeIndex([d.date for d in benchmark_data])

        returns['Benchmark.Returns']  = pd.Series([d.returns for d in benchmark_data], index=dates)
        returns['Benchmark.CReturns'] = ((returns['Benchmark.Returns'] + 1).cumprod()) - 1
        returns['Returns']            = pd.Series(self.results.returns, index=dates)
        returns['CReturns']           = pd.Series(((self.results.returns + 1).cumprod()) - 1, index=dates)

        df = pd.DataFrame(returns, index=dates)

        if save:
            raise NotImplementedError()
            self.feeds.stock_db.saveDFToDB(df, table=db_id)

        if benchmark is None:
            df = df.drop(['Benchmark.Returns', 'Benchmark.CReturns'], axis=1)
        return df

    def _get_index(self, perfs):
        #NOTE No frequency infos or just period number ?
        start = pytz.utc.localize(pd.datetime.strptime(perfs[0]['period_label'] + '-01', '%Y-%m-%d'))
        end = pytz.utc.localize(pd.datetime.strptime(perfs[-1]['period_label'] + '-01', '%Y-%m-%d'))
        return pd.date_range(start - pd.datetools.BDay(10), end, freq=pd.datetools.MonthBegin())

    def _extract_perf(self, perfs, field):
        index = self._get_index(perfs)
        values = [perfs[i][field] for i in range(len(perfs))]
        return pd.Series(values, index=index)

    def __del__(self):
        del self.server
        #self.server.socket.close()
        #self.server.context.term()
