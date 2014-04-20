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
from intuition.data.loader import LiveBenchmark
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
    context = None

    def _get_benchmark_handler(self, last_trade, freq='minutely'):
        '''
        Setup a custom benchmark handler or let zipline manage it
        '''
        return LiveBenchmark(
            last_trade, frequency=freq).surcharge_market_data \
            if utils.is_live(last_trade) else None

    def configure_environment(self, last_trade, benchmark, timezone):
        ''' Prepare benchmark loader and trading context '''

        if last_trade.tzinfo is None:
            last_trade = pytz.utc.localize(last_trade)

        # Setup the trading calendar from market informations
        self.benchmark = benchmark
        self.context = TradingEnvironment(
            bm_symbol=benchmark,
            exchange_tz=timezone,
            load=self._get_benchmark_handler(last_trade))

    def build(self, identity, modules, strategy=constants.DEFAULT_CONFIG):
        '''
        Wrapper of zipline run() method. Use the configuration set so far
        to build up the trading environment
        '''
        # TODO Catch a problem here
        self.engine = TradingEngine(identity, modules, strategy)
        self.initial_cash = strategy['manager'].get('cash', None)

    def __call__(self, datafeed, auto=False):
        ''' wrap zipline.run() with finer control '''
        self.engine.auto = auto
        # FIXME crash if trading one day that is not a trading day
        with self.context:
            sim_params = create_simulation_parameters(
                capital_base=self.initial_cash,
                start=datafeed.start,
                end=datafeed.end)

            daily_stats = self.engine.run(datafeed, sim_params)

        return Analyze(
            params=sim_params,
            results=daily_stats,
            metrics=self.engine.risk_report,
            benchmark=self.benchmark)
