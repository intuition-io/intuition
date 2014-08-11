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
from zipline.utils.factory import create_simulation_parameters
import intuition.constants as constants
import intuition.data.loader as loader
from intuition.core.analyzes import Analyze
import intuition.utils as utils
from intuition.errors import InvalidEngine

log = dna.logging.logger(__name__)


class TradingEngine(object):
    ''' Dynamically loaded class wrapping zipline Backtester, returns the
    requested algo ready for use '''

    def __new__(self, identity, sim_params, modules, strategy_conf):

        if 'algorithm' not in modules:
            raise InvalidEngine(
                id=identity, reason='no algorithm module provided')

        algo_obj = utils.intuition_module(modules['algorithm'])
        trading_algo = algo_obj(
            identity=identity,
            sim_params=sim_params,
            properties=strategy_conf.get('algorithm', {})
        )

        trading_algo.set_logger(dna.logging.logger('algo.' + identity))
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

    def configure_environment(self, datafeed, capital, benchmark, timezone):
        ''' Prepare benchmark loader and trading context '''
        last_trade = datafeed.end
        if last_trade.tzinfo is None:
            last_trade = pytz.utc.localize(last_trade)

        self.sim_params = create_simulation_parameters(
            capital_base=capital,
            sids=datafeed.sids,
            start=datafeed.start,
            end=datafeed.end
        )

        # Setup the trading calendar from market informations
        self.benchmark = benchmark
        self.trading_context = TradingEnvironment(
            bm_symbol=benchmark,
            exchange_tz=timezone,
            load=self._benchmark_handler(last_trade)
        )

        self.datafeed = datafeed

    def __call__(self, identity, modules, strategy=None):
        ''' Wrap zipline.run() with finer control '''
        # FIXME crash if trading one day that is not a trading day
        strategy = strategy or constants.DEFAULT_CONFIG
        with self.trading_context:
            self.engine = TradingEngine(
                identity, self.sim_params, modules, strategy
            )
            daily_stats = self.engine.run(
                self.datafeed, overwrite_sim_params=False
            )

        # TODO Use zipline self.analyze hook instead
        return Analyze(
            # Safer to access internal sim_params as there are several methods
            # to get the structure setup
            params=self.engine.sim_params,
            results=daily_stats,
            metrics=self.engine.risk_report,
            benchmark=self.benchmark
        )
