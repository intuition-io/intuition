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

from neuronquant.data.datafeed import DataFeed
from neuronquant.ai.managers import Constant, Equity, OptimalFrontier
#from neuronquant.network.transport import ZMQ_Dealer
import neuronquant.utils.datautils as datautils
from neuronquant.data.ziplinesources.loader import LiveBenchmark
#from neuronquant.data.ziplinesources.live.equities import DataLiveSource
from neuronquant.gears.analyzes import Analyzes

import pytz
import pandas as pd

#from qstkutil import tsutil as tsu

import logbook
log = logbook.Logger('Engine')

from zipline.finance.trading import SimulationParameters, TradingEnvironment


class BacktesterEngine(object):
    ''' Factory class wrapping zipline Backtester, returns the requested algo ready for use '''
    algorithms = {'DualMA'      : DualMovingAverage       , 'Momentum'   : Momentum,
                  'VWAP'        : VolumeWeightAveragePrice, 'BuyAndHold' : BuyAndHold,
                  'StdBased'    : StddevBased             , 'OLMAR'      : OLMAR,
                  'MultiMA'     : MultiMA                 , 'MACrossover': MovingAverageCrossover}

    portfolio_managers = {'Equity': Equity, 'Constant': Constant, 'OptimalFrontier': OptimalFrontier}

    def __new__(self, algo, manager, strategie_configuration):
        '''
        Reads the user configuration and returns
        '''
        # CHecking if algorithm and manager the user asks for are available
        if algo not in BacktesterEngine.algorithms:
            raise NotImplementedError('Algorithm {} not available or implemented'.format(algo))
        log.info('Algorithm {} available, getting a reference to it.'.format(algo))

        if manager not in BacktesterEngine.portfolio_managers:
            raise NotImplementedError('Manager {} not available or implemented'.format(manager))
        log.info('Manager {} available, getting a reference and initializing it.'.format(manager))

        #NOTE Other params: annualizer (default is cool), capital_base, sim_params (both are set in run function)
        trading_algorithm = BacktesterEngine.algorithms[algo](strategie_configuration['algorithm'])

        trading_algorithm.set_logger(logbook.Logger(algo))

        # Linking to the algorithm the configured portfolio manager
        trading_algorithm.manager = BacktesterEngine.portfolio_managers[manager](strategie_configuration['manager'])

        # If requested and possible, load the named portfolio to start trading with it
        #FIXME Works, but every new event resets the portfolio
        portfolio_name = strategie_configuration['manager'].get('name')

        if strategie_configuration['manager'].get('load_backup', False) and portfolio_name:
            log.info('Re-loading last {} portfolio from database'.format(portfolio_name))
            ## Retrieving a zipline portfolio object. str() is needed as the parameter is of type unicode
            backup_portfolio = trading_algorithm.manager.load_portfolio(str(portfolio_name))

            if backup_portfolio is None:
                log.warning('! Unable to set {} portfolio: not found'.format(portfolio_name))
            else:
                trading_algorithm.set_portfolio(backup_portfolio)
                log.info('Portfolio setup successfull')

        return trading_algorithm


#NOTE engine.feed_data(tickers, start, end, freq) ? using set_source()
class Simulation(object):
    ''' Take a trading strategie and evalute its results '''
    def __init__(self, data=None):
        #NOTE Allowing different data access ?
        #self.metrics = None
        #self.server        = ZMQ_Dealer(id=self.__class__.__name__)
        self.datafeed = DataFeed()

    #TODO For both, timezone configuration
    def configure(self, configuration):
        '''
        Prepare dates, data, trading environment for simulation
        _______________________________________________________
        Parameters
            configuration: dict()
                Structure with previously defined backtest behavior
        '''
        data = self._configure_data(tickers    = configuration['tickers'],
                                  start_time = configuration['start'],
                                  end_time   = configuration['end'],
                                  freq       = configuration['frequency'],
                                  exchange   = configuration['exchange'],
                                  live       = configuration['live'])

        context = self._configure_context(configuration['exchange'])

        return data, context

    #NOTE Should the data be loaded in zipline sourcedata class ?
    def _configure_data(self, tickers, start_time=None, end_time=pd.datetime.now(pytz.utc), freq='daily', exchange='', live=False):
        if live:
            # Default end_date is now, suitable for live trading
            self.load_market_data = LiveBenchmark(end_time, frequency=freq).load_market_data

            #dates = pd.date_range(start_time, end_time, freq=freq)
            #NOTE A temporary hack to avoid zipline dirty modification
            periods = end_time - start_time
            dates = datautils.filter_market_hours(pd.date_range(pd.datetime.now(), periods=periods.days + 1,
                                                                freq='1min'),
                                                                #TODO ...hard coded, later: --frequency daily,3
                                                  exchange)
            #dates = datautils.filter_market_hours(dates, exchange)
            if len(dates) == 0:
                log.warning('! Market closed.')
                sys.exit(0)
            data = {'stream_source' : exchange,
                    'tickers'       : tickers,
                    'index'         : dates.tz_localize(pytz.utc)}
        else:
            # Use default zipline load_market_data, i.e. data from msgpack files in ~/.zipline/data/
            self.load_market_data = None

            #TODO if start_time is None get default start_time in ~/.quantrade/default.json
            assert start_time
            # Fetch data from mysql database
            data = self.datafeed.quotes(tickers,
                                     start_date = start_time,
                                     end_date   = end_time)
            if len(data) == 0:
                log.warning('Got nothing from database')
                data = pd.DataFrame()
            else:
                assert isinstance(data, pd.DataFrame)
                assert data.index.tzinfo

        return data

    def set_becnhmark_loader(self, load_function):
        self.load_market_data = load_function

    #TODO Use of futur localisation database criteria
    #TODO A list of markets to check if this one is in
    def _configure_context(self, exchange=''):
        '''
        Setup from exchange traded on benchmarks used, location
        and method to load data market while simulating
        _______________________________________________
        Parameters
            exchange: str
                Trading exchange market
        '''
        # Environment configuration
        if exchange in datautils.Exchange:
            finance_context = TradingEnvironment(bm_symbol   = datautils.Exchange[exchange]['index'],
                                                 exchange_tz = datautils.Exchange[exchange]['timezone'],
                                                 load        = self.load_market_data)
        else:
            raise NotImplementedError('Because of computation limitation, trading worldwide not permitted currently')

        return finance_context

    def run(self, data, configuration, strategie, context):
        #___________________________________________________________________________    Running    ________
        log.info('\n-- Running backetester...\nUsing algorithm: {}\n'.format(configuration['algorithm']))
        log.info('\n-- Using portfolio manager: {}\n'.format(configuration['manager']))

        backtester = BacktesterEngine(configuration['algorithm'],
                                      configuration['manager'],
                                      strategie)

        #NOTE This method does not change anything
        #backtester.set_sources([DataLiveSource(data_tmp)])
        #TODO A new command line parameter ? only minutely and daily (and hourly normally) Use filter parameter of datasource ?
        backtester.set_data_frequency(configuration['frequency'])

        # Running simulation with it
        with context:
            results, monthly_perfs = backtester.run(data,
                                                    SimulationParameters(capital_base = configuration['cash'],
                                                                         period_start = configuration['start'],
                                                                         period_end   = configuration['end']))

        #return self.results
        return Analyzes(results=results, metrics=monthly_perfs, datafeed=self.datafeed, configuration=configuration)
