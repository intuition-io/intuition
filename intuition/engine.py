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
import intuition.utils as utils
from intuition.errors import InvalidEngine
import intuition.api.datafeed as datafeed

log = dna.logging.logger(__name__)


def check_setup(func):
    def inner(*args, **kwargs):
        self = args[0]
        session = args[1]
        if self.data is None:
            raise InvalidEngine(id=session, reason='No data module loaded')
        if self._algo_klass is None:
            raise InvalidEngine(id=session, reason='No algo module loaded')
        if self.env is None:
            raise InvalidEngine(id=session, reason='Env not configured')
        self.data.check_sources()
        if self.analyzer is None:
            self.load_analyzer()
        log.info('Engine setup validated')
        return func(*args, **kwargs)
    return inner


def benchmark_handler(last_trade, freq='daily'):
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
    log.info('Set benchmarke handler', benchmark=benchmark_handler)
    return benchmark_handler


class Env(object):
    ''' Doc '''
    def __init__(self, sim_params, trading_context):
        self.sim_params = sim_params
        self.trading_context = trading_context

    def __call__(self):
        return self.trading_context
      

class Core(object):
    ''' Setup and trigger trading sessions '''

    def __init__(self, capital, timeline, market):
        self.capital = capital
        self.timeline = timeline
        self.market = market
        log.info('New Core simulator',
                 capital=capital,
                 market=market)

        # Modules
        self.data = None
        self.analyzer = None
        self._algo_klass = None
        self.backtest_source = None
        self.live_source = None
        self.env = None

    def load_data(self, frequency=None):
        log.info('Load data module', module='HybridDataFactory')
        frequency = frequency or constants.DEFAULT_FREQUENCY
        self.data = datafeed.HybridDataFactory(
            self.timeline, self.market, frequency
        )

    def configure_environment(self):
        ''' Prepare benchmark loader and trading context '''
        last_trade = self.data.end
        if last_trade.tzinfo is None:
            last_trade = pytz.utc.localize(last_trade)

        sim_params = create_simulation_parameters(
            capital_base=self.capital,
            sids=self.data.sids,
            start=self.data.start,
            end=self.data.end
        )

        # Setup the trading calendar from market informations
        trading_context = TradingEnvironment(
            bm_symbol=self.market.benchmark,
            exchange_tz=self.market.timezone,
            load=benchmark_handler(last_trade)
        )
        log.info('Setup engine environment',
                 params=sim_params, context=trading_context)
        self.env = Env(sim_params, trading_context)

    def load_analyzer(self, path='intuition.api.analysis.Basic'):
        log.info('Load analyzer module', module=path)
        self.analyzer = utils.intuition_module(path)

    def load_algorithm(self, path, **kwargs):
        log.info('Load algorithm module', module=path)
        self._algo_klass = utils.intuition_module(path)
        self._algo_strategy = kwargs

    @check_setup
    def __call__(self, identity):
        ''' Safely wrap zipline.run() with our configuration '''
        # FIXME crash if trading one day that is not a trading day
        with self.env():
            log.debug('Instanciate engine', properties=self._algo_strategy)
            engine = self._algo_klass(
                identity=identity,
                sim_params=self.env.sim_params,
                properties=self._algo_strategy
            )
            engine.set_logger(dna.logging.logger('algo.{}'.format(identity)))
            log.info('Run engine with provided data module')
            stats = engine.run(self.data, overwrite_sim_params=False)

        log.info('Done, return result analysis')
        # A fallback is available so that it stays optional
        return self.analyzer(
            stats,  # Pretty much everything that appened, daily
            engine.perf_tracker.cumulative_risk_metrics
        )
