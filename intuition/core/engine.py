# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Intuition engine
  ----------------

  Wraps zipline engine and results with more configuration options

  :copyright (c) 2014 Xavier Bruhiere
  :license: Apache 2.0, see LICENSE for more details.
'''


import pytz
import dna.utils
import dna.logging
from zipline.finance.trading import TradingEnvironment
import intuition.constants as constants
import intuition.data.loader as loader
from intuition.core.analyzes import Analyze
import intuition.utils as utils
from intuition.errors import InvalidEngine

log = dna.logging.logger(__name__)


# NOTE Is there still a point to use here a constructor object instead of a
#     simple function ?
class TradingEngine(object):
    ''' Factory class wrapping zipline Backtester, returns the requested algo
    ready for use '''

    def __new__(self, identity, modules, strategy_conf):

        if 'algorithm' not in modules:
            raise InvalidEngine(
                id=identity, reason='no algorithm module provided')

        algo_obj = utils.intuition_module(modules['algorithm'])
        trading_algo = algo_obj(
            identity=identity,
            capital_base=strategy_conf.get('manager', {}).get('cash'),
            properties=strategy_conf.get('algorithm', {})
        )

        trading_algo.set_logger(dna.logging.logger('algo.' + identity))

        # Use a portfolio manager
        if modules.get('manager'):
            log.info('initializing manager {}'.format(modules['manager']))
            # Linking to the algorithm the configured portfolio manager
            trading_algo.manager = utils.intuition_module(modules['manager'])(
                strategy_conf.get('manager', {}))
        else:
            trading_algo.manager = None
            log.info('no portfolio manager used')

        return trading_algo


class Simulation(object):
    ''' Setup and trigger trading sessions '''
    trading_context = None

    def _benchmark_handler(self, last_trade, freq='daily'):
        '''
        Setup a custom benchmark handler or let zipline manage it
        '''
        benchmark_handler = None
        if not dna.utils.is_online():
            benchmark_handler = loader.OfflineBenchmark(
                frequency=freq
            ).surcharge_market_data
        elif utils.is_live(last_trade):
            benchmark_handler = loader.LiveBenchmark(
                frequency=freq
            ).surcharge_market_data
        return benchmark_handler

    def configure_environment(self, last_trade, benchmark, timezone):
        ''' Prepare benchmark loader and trading context '''

        if last_trade.tzinfo is None:
            last_trade = pytz.utc.localize(last_trade)

        # Setup the trading calendar from market informations
        self.benchmark = benchmark
        self.trading_context = TradingEnvironment(
            bm_symbol=benchmark,
            exchange_tz=timezone,
            load=self._benchmark_handler(last_trade)
        )

    def __call__(self, identity, datafeed, modules, strategy=None):
        ''' wrap zipline.run() with finer control '''
        # FIXME crash if trading one day that is not a trading day
        strategy = strategy or constants.DEFAULT_CONFIG
        with self.trading_context:
            self.engine = TradingEngine(identity, modules, strategy)
            daily_stats = self.engine.run(datafeed, overwrite_sim_params=True)

        return Analyze(
            # Safer to access internal sim_params as there are several methods
            # to get the structure setup
            params=self.engine.sim_params,
            results=daily_stats,
            metrics=self.engine.risk_report,
            benchmark=self.benchmark
        )
