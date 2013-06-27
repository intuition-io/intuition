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


import sys
import pytz
import pandas as pd
import logbook
log = logbook.Logger('Engine')

from neuronquant.data.datafeed import DataFeed
import neuronquant.utils.datautils as datautils
from neuronquant.data.ziplinesources.loader import LiveBenchmark
from neuronquant.gears.analyzes import Analyze

from zipline.finance.trading import TradingEnvironment
from zipline.utils.factory import create_simulation_parameters

import neuronquant.strateg_library as library


BASE_CONFIG = {'algorithm': {}, 'manager': {}}


class BacktesterEngine(object):
    ''' Factory class wrapping zipline Backtester, returns the requested algo ready for use '''

    def __new__(self, algo, manager=None, source=None, strategie_configuration=BASE_CONFIG):
        '''
        Reads the user configuration and returns
        '''
        library.check_availability(algo, manager, source)

        #NOTE Other params: annualizer (default is cool), capital_base, sim_params (both are set in run function)
        trading_algorithm = library.algorithms[algo](
            properties=strategie_configuration['algorithm'])
            #capital_base=10000.0, data_frequency='minute')

        portfolio_name = strategie_configuration['manager'].get('name', 'ChuckNorris')
        trading_algorithm.set_logger(logbook.Logger('Algo::' + portfolio_name))

        if source:
            trading_algorithm.set_data_generator(library.data_sources[source])

        # Use of a portfolio manager
        if manager:
            log.info('Initializing Manager')
            # Linking to the algorithm the configured portfolio manager
            trading_algorithm.manager = library.portfolio_managers[manager](
                strategie_configuration['manager'])

            # If requested and possible, load the named portfolio to start trading with it
            #FIXME Works, but every new event resets the portfolio

            if strategie_configuration['manager'].get('load_backup', False) and portfolio_name:
                log.info('Re-loading last {} portfolio from database'.format(portfolio_name))
                # Retrieving a zipline portfolio object. str() is needed as the parameter is of type unicode
                backup_portfolio = trading_algorithm.manager.load_portfolio(str(portfolio_name))

                if backup_portfolio is None:
                    log.warning('! Unable to set {} portfolio: not found'.format(portfolio_name))
                else:
                    trading_algorithm.set_portfolio(backup_portfolio)
                    log.info('Portfolio setup successful')
        else:
            trading_algorithm.manager = None
            log.info('No portfolio manager used')

        return trading_algorithm


#NOTE engine.feed_data(tickers, start, end, freq) ? using set_source()
class Simulation(object):
    ''' Take a trading strategie and evalute its results '''
    def __init__(self, configuration):
        #NOTE Allowing different data access ?
        #self.metrics = None
        #self.server        = ZMQ_Dealer(id=self.__class__.__name__)
        self.configuration = configuration
        if 'quandl' in configuration['env']:
            self.datafeed = DataFeed(configuration['env']['quandl'])
        else:
            self.datafeed = DataFeed()

    #TODO For both, timezone configuration
    def configure(self):
        '''
        Prepare dates, data, trading environment for simulation
        _______________________________________________________
        Parameters
            configuration: dict()
                Structure with previously defined backtest behavior
        '''
        data = self._configure_data(tickers    = self.configuration['tickers'],
                                    start_time = self.configuration['start'],
                                    end_time   = self.configuration['end'],
                                    freq       = self.configuration['frequency'],
                                    #source     = self.configuration['source'],
                                    exchange   = self.configuration['exchange'],
                                    live       = self.configuration['live'])

        context = self._configure_context(self.configuration['exchange'])

        return data, context

    #NOTE Should the data be loaded in zipline sourcedata class ?
    #FIXME data default not suitable for live mode
    def _configure_data(self, tickers, start_time = pd.datetime.now(pytz.utc),
                                       end_time   = pd.datetime.now(pytz.utc),
                                       freq='daily', exchange='', live=False):
        assert start_time != end_time

        if live:
            # Check that start_time is now or later
            assert start_time > pd.datetime.now() - pd.datetools.Second(5)
            # Default end_date is now, not suitable for live trading
            self.load_market_data = LiveBenchmark(end_time, frequency=freq).load_market_data
            #TODO ...hard coded, later for exemple: --frequency daily,3
            data_freq = '1min'
        else:
            # Use default zipline load_market_data, i.e. data from msgpack files in ~/.zipline/data/
            self.load_market_data = None
            data_freq = 'D'

            # Use datafeed object to retrieve data
            #data = self._get_data(tickers, start_time, end_time)

        dates = datautils.filter_market_hours(pd.date_range(start_time,
                                                            end_time,
                                                            freq=data_freq),
                                              exchange)

        if len(dates) == 0:
            log.warning('! Market closed.')
            sys.exit(0)

        data = {'stream_source': exchange,
                'tickers'      : tickers,
                'index'        : dates}

        return data

    '''
    def _get_data(self, tickers, start_date, end_date):
        self.implemented_sources = ['mysql', 'quandl', 'csv']
        for source in self.implemented_sources:
            data = self._try(source, tickers, start_date=start_date, end_date=end_date)
            if data.empty:
                log.warning('Got nothing from {}'.format(source))
                data = pd.DataFrame()
            else:
                assert isinstance(data, pd.DataFrame)
                assert data.index.tzinfo
                break

        return data

    def _try(self, source, tickers, **kwargs):
        if source == 'mysql':
            data = self.datafeed.quotes(tickers, **kwargs)
        elif source == 'csv':
            raise NotImplementedError()
        elif source == 'quandl':
            data = self.datafeed.fetch_quandl(tickers, returns='pandas', **kwargs)
        else:
            raise NotImplementedError()
        return data
    '''

    def set_becnhmark_loader(self, load_function):
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
            trading_context = TradingEnvironment(bm_symbol   = datautils.Exchange[exchange]['index'],
                                                 exchange_tz = datautils.Exchange[exchange]['timezone'],
                                                 load        = self.load_market_data)
        else:
            raise NotImplementedError('Because of computation limitation, \
                trading worldwide not permitted currently')

        return trading_context

    def run(self, data, configuration, strategie, context):
        log.info('\n-- Running backetester...\nUsing algorithm: {}\n'.format(configuration['algorithm']))
        log.info('\n-- Using portfolio manager: {}\n'.format(configuration['manager']))

        backtester = BacktesterEngine(configuration['algorithm'],
                                      configuration['manager'],
                                      configuration['source'],
                                      strategie)

        #NOTE This method does not change anything
        #backtester.set_sources([DataLiveSource(data_tmp)])
        #TODO A new command line parameter ? only minutely and daily (and hourly normally) Use filter parameter of datasource ?
        backtester.set_data_frequency(configuration['frequency'])

        # Running simulation with it
        with context:
            sim_params = create_simulation_parameters(capital_base = configuration['cash'],
                                                      start = configuration['start'],
                                                      end   = configuration['end'])

            results, monthly_perfs = backtester.run(data,
                                                    sim_params=sim_params)

        return Analyze(results=results, metrics=monthly_perfs, datafeed=self.datafeed, configuration=configuration)
