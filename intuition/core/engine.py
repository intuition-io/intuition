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


import pytz
import pandas as pd
import logbook

from zipline.finance.trading import TradingEnvironment
from zipline.utils.factory import create_simulation_parameters

from intuition import modules_path, default_config
from intuition.data.utils import Exchanges
from intuition.data.loader import LiveBenchmark
from intuition.core.analyzes import Analyze
import intuition.utils.utils as utils


log = logbook.Logger('intuition.core.engine')


def _intuition_module(location):
    location = location.split('.')
    obj = location.pop(-1)
    path = '.'.join([modules_path] + location)
    return utils.dynamic_import(path, obj)


class TradingEngine(object):
    ''' Factory class wrapping zipline Backtester, returns the requested algo
    ready for use '''

    def __new__(self, identity, modules, strategy_conf=default_config):

        algo_obj = _intuition_module(modules['algorithm'])
        algo_obj.identity = identity
        trading_algo = algo_obj(properties=strategy_conf['algorithm'])

        trading_algo.set_logger(logbook.Logger('algo.' + identity))

        if modules['data']:
            trading_algo.set_data_generator(_intuition_module(modules['data']))

        # Use a portfolio manager
        if modules['manager']:
            log.info('initializing manager {}'.format(modules['manager']))
            # Linking to the algorithm the configured portfolio manager
            trading_algo.manager = _intuition_module(modules['manager'])(
                strategy_conf['manager'])
        else:
            trading_algo.manager = None
            log.info('no portfolio manager used')

        return trading_algo


class Simulation(object):
    ''' Take a trading strategy and evalute its results '''

    def __init__(self, configuration):
        self.configuration = configuration
        self.context = None

    def configure(self):
        '''
        Prepare dates, data, trading environment for simulation
        '''
        last_trade = self.configuration['index'][-1]
        if last_trade > pd.datetime.now(pytz.utc):
            # This is live trading
            self.set_benchmark_loader(LiveBenchmark(
                last_trade, frequency='minute').surcharge_market_data)
        else:
            self.set_benchmark_loader(None)

        self.context = self._configure_context(self.configuration['exchange'])

    def set_benchmark_loader(self, load_function):
        self.load_market_data = load_function

    def _configure_context(self, exchange=''):
        '''
        Setup from exchange traded on benchmarks used, location
        and method to load data market while simulating
        '''
        # Environment configuration
        if exchange in Exchanges:
            trading_context = TradingEnvironment(
                bm_symbol=Exchanges[exchange]['symbol'],
                exchange_tz=Exchanges[exchange]['timezone'],
                load=self.load_market_data)
        else:
            raise NotImplementedError('Because of computation limitation, \
                trading worldwide not permitted currently')

        return trading_context

    def run(self, identity, data, strategy):
        engine = TradingEngine(identity,
                               self.configuration['modules'],
                               strategy)

        #NOTE This method does not change anything
        #engine.set_sources([DataLiveSource(data_tmp)])
        #TODO A new command line parameter ? only minutely and daily
        #     (and hourly normaly) Use filter parameter of datasource ?
        #engine.set_data_frequency(self.configuration['frequency'])
        engine.is_live = self.configuration['live']

        # Running simulation with it
        #FIXME crash if trading one day that is not a trading day
        with self.context:
            sim_params = create_simulation_parameters(
                capital_base=strategy['manager']['cash'],
                start=self.configuration['index'][0],
                end=self.configuration['index'][-1])

            daily_stats = engine.go(data, sim_params=sim_params)

        return Analyze(
            results=daily_stats,
            metrics=engine.risk_report,
            configuration=self.configuration)
