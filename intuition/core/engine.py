#
# Copyright 2013 Xavier Bruhiere
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


import sys
import pytz
import pandas as pd
import logbook

import intuition.data.utils as datautils
from intuition.modules.sources.loader import LiveBenchmark
from intuition.core.analyzes import Analyze
from intuition.data.utils import filter_market_hours

from zipline.finance.trading import TradingEnvironment
from zipline.utils.factory import create_simulation_parameters

import intuition.modules.library as library


BASE_CONFIG = {'algorithm': {}, 'manager': {}}
DEFAULT_PORTFOLIO_NAME = 'ChuckNorris'
log = logbook.Logger('intuition.core.engine')


class TradingEngine(object):
    ''' Factory class wrapping zipline Backtester, returns the requested algo
    ready for use '''

    def __new__(self, algo, manager=None, source=None,
                strategy_configuration=BASE_CONFIG):
        '''
        Reads the user configuration and returns
        '''
        library.check_availability(algo, manager, source)

        #NOTE Other params: annualizer (default is cool), capital_base,
        #     data_frequency, sim_params (both are set in run function)
        trading_algorithm = library.algorithms[algo](
            properties=strategy_configuration['algorithm'])

        portfolio_name = strategy_configuration['manager'].get(
            'name', DEFAULT_PORTFOLIO_NAME)
        trading_algorithm.set_logger(logbook.Logger('algo.' + portfolio_name))

        if source:
            trading_algorithm.set_data_generator(library.data_sources[source])

        # Use of a portfolio manager
        if manager:
            log.info('initializing Manager')
            # Linking to the algorithm the configured portfolio manager
            trading_algorithm.manager = library.portfolio_managers[manager](
                strategy_configuration['manager'])

            # If requested and possible, loads the named portfolio to start
            # trading with it
            #FIXME Works, but every new event resets the portfolio

            if strategy_configuration['manager'].get('load_backup', False) \
                    and portfolio_name:

                log.info('Re-loading last {} portfolio from database'
                         .format(portfolio_name))
                # Retrieving a zipline portfolio object. str() is needed as the
                # parameter is of type unicode
                backup_portfolio = trading_algorithm.manager.load_portfolio(
                    str(portfolio_name))

                if backup_portfolio is None:
                    log.warning('! Unable to set {} portfolio: not found'
                                .format(portfolio_name))
                else:
                    trading_algorithm.set_portfolio(backup_portfolio)
                    log.info('Portfolio setup successful')
        else:
            trading_algorithm.manager = None
            log.info('no portfolio manager used')

        return trading_algorithm


#NOTE engine.feed_data(universe, start, end, freq) ? using set_source()
class Simulation(object):
    ''' Take a trading strategy and evalute its results '''

    def __init__(self, configuration):
        #self.server        = ZMQ_Dealer(id=self.__class__.__name__)
        self.configuration = configuration
        self.context = None

    #TODO For both, timezone configuration
    def configure(self):
        '''
        Prepare dates, data, trading environment for simulation
        '''
        data = self._configure_data(universe=self.configuration['universe'],
                                    start_time=self.configuration['start'],
                                    end_time=self.configuration['end'],
                                    freq=self.configuration['frequency'],
                                    exchange=self.configuration['exchange'],
                                    live=self.configuration['live'])

        self.context = self._configure_context(self.configuration['exchange'])

        return data

    #NOTE Should the data be loaded in zipline sourcedata class ?
    #FIXME data default not suitable for live mode
    def _configure_data(self, universe, start_time=pd.datetime.now(pytz.utc),
                        end_time=pd.datetime.now(pytz.utc),
                        freq='daily', exchange='', live=False):
        assert start_time != end_time

        if live:
            # Check that start_time is now or later
            tolerance = pd.datetools.Second(5)
            if (start_time < (pd.datetime.now(pytz.utc) - tolerance)):
                log.warning('! Invalid start time, setting it to now')
                start_time = pd.datetime.now(pytz.utc)
            # Default end_date is now, not suitable for live trading
            #self.set_benchmark_loader(None)
            self.set_benchmark_loader(
                LiveBenchmark(end_time, frequency=freq).surcharge_market_data)
            #TODO ...hard coded, later for exemple: --frequency daily,3
            data_freq = '1min'

        else:
            # Use default zipline load_market_data, i.e. data from msgpack
            # files in ~/.zipline/data/
            self.set_benchmark_loader(None)
            data_freq = 'D'

        dates = filter_market_hours(pd.date_range(start_time,
                                                  end_time,
                                                  freq=data_freq),
                                    exchange)

        if len(dates) == 0:
            log.warning('! Market closed.')
            sys.exit(0)

        data = {'stream_source': exchange,
                'universe': universe,
                'index': dates}

        return data

    def set_benchmark_loader(self, load_function):
        self.load_market_data = load_function

    #TODO Use of futur localisation database criteria
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
            trading_context = TradingEnvironment(
                bm_symbol=datautils.Exchange[exchange]['index'],
                exchange_tz=datautils.Exchange[exchange]['timezone'],
                load=self.load_market_data)
        else:
            raise NotImplementedError('Because of computation limitation, \
                trading worldwide not permitted currently')

        return trading_context

    def run(self, data, strategy):
        log.info('\n-- Running backetester...\nUsing algorithm: {}\n'
                 .format(self.configuration['algorithm']))
        log.info('\n-- Using portfolio manager: {}\n'
                 .format(self.configuration['manager']))

        engine = TradingEngine(self.configuration['algorithm'],
                               self.configuration['manager'],
                               self.configuration['source'],
                               strategy)

        #NOTE This method does not change anything
        #engine.set_sources([DataLiveSource(data_tmp)])
        #TODO A new command line parameter ? only minutely and daily
        #     (and hourly normally) Use filter parameter of datasource ?
        #engine.set_data_frequency(self.configuration['frequency'])
        engine.is_live = self.configuration['live']

        # Running simulation with it
        #FIXME crash if trading one day that is not a trading day
        with self.context:
            sim_params = create_simulation_parameters(
                capital_base=self.configuration['cash'],
                start=self.configuration['start'],
                end=self.configuration['end'])

            daily_stats = engine.go(data, sim_params=sim_params)

        return Analyze(
            results=daily_stats,
            metrics=engine.risk_report,
            #datafeed=self.datafeed,
            datafeed=None,
            configuration=self.configuration)
