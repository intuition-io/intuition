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

import intuition.constants as constants
from intuition.data.utils import Exchanges
from intuition.data.loader import LiveBenchmark
from intuition.core.analyzes import Analyze
import intuition.utils.utils as utils


log = logbook.Logger('intuition.core.engine')


def _intuition_module(location):
    ''' Build the module path and import it '''
    path = location.split('.')
    obj = path.pop(-1)
    return utils.dynamic_import('.'.join(path), obj)


#NOTE Is there still a point to use here a constructor object instead of a
#     simple function ?
class TradingEngine(object):
    ''' Factory class wrapping zipline Backtester, returns the requested algo
    ready for use '''

    def __new__(self, identity, modules, strategy_conf):

        algo_obj = _intuition_module(modules['algorithm'])
        algo_obj.identity = identity
        trading_algo = algo_obj(properties=strategy_conf['algorithm'])

        trading_algo.set_logger(logbook.Logger('algo.' + identity))

        if modules['data']:
            trading_algo.set_data_generator(_intuition_module(modules['data']))

        # Use a portfolio manager
        if modules.get('manager'):
            log.info('initializing manager {}'.format(modules['manager']))
            # Linking to the algorithm the configured portfolio manager
            trading_algo.manager = _intuition_module(modules['manager'])(
                strategy_conf['manager'])
        else:
            trading_algo.manager = None
            log.info('no portfolio manager used')

        return trading_algo


class Simulation(object):
    ''' Setup and trigger trading sessions '''
    context = None

    def _get_benchmark_handler(self, last_trade):
        '''
        Setup a custom benchmark handler or let zipline manage it
        '''
        is_live = (last_trade > pd.datetime.now(pytz.utc))
        #NOTE minute hardcoded until more timedeltas supported
        return LiveBenchmark(
            last_trade, frequency='minute').surcharge_market_data \
            if is_live else None

    def configure_environment(self, last_trade, exchange):
        ''' Prepare benchmark loader and trading context '''

        # Setup the trading calendar from market informations
        if exchange in Exchanges:
            self.context = TradingEnvironment(
                bm_symbol=Exchanges[exchange]['symbol'],
                exchange_tz=Exchanges[exchange]['timezone'],
                load=self._get_benchmark_handler(last_trade))
        else:
            raise NotImplementedError('Because of computation limitation, \
                trading worldwide not permitted currently')

    def build(self, identity, modules, strategy=constants.DEFAULT_CONFIG):
        '''
        Wrapper of zipline run() method. Use the configuration set so far
        to build up the trading environment and launch the system
        '''
        self.engine = TradingEngine(identity, modules, strategy)

        self.initial_cash = strategy['manager'].get('cash', None)

    def run(self, data, auto=False):
        ''' wrap zipline.run() with finer control '''
        self.engine.auto = auto
        #FIXME crash if trading one day that is not a trading day
        with self.context:
            sim_params = create_simulation_parameters(
                capital_base=self.initial_cash,
                start=data['index'][0],
                end=data['index'][-1])

            daily_stats = self.engine.trade(data, sim_params=sim_params)

        return Analyze(
            results=daily_stats,
            metrics=self.engine.risk_report)
