# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Intuition alogirthm api
  -----------------------

  Trading algorithms factory. Everything that can extend in a useful way
  zipline.TradingAlgorithm goes here. Future algorithms should inherit from
  this class.

  :copyright (c) 2014 Xavier Bruhiere
  :license: Apache 2.0, see LICENSE for more details.
'''


import abc
from copy import copy
import zipline.algorithm
import intuition.errors
import intuition.utils


# pylint: disable=R0921
class TradingFactory(zipline.algorithm.TradingAlgorithm):
    '''
    Intuition surcharge of main zipline class, but fully compatible.
    '''

    __metaclass__ = abc.ABCMeta
    # Up to us to say when the algorithm is initialized
    AUTO_INITIALIZE = False

    def __init__(self, sim_params, identity='johndoe', properties=None):
        # Attributes initialization
        self.middlewares = []
        self.identity = identity

        # User customized attributes
        safe_properties = properties or {}
        kwargs = {
            'sim_params': sim_params,
            # Set algo capital to the same value as portfolio cash
            'capital_base': sim_params.capital_base,
            'instant_fill': safe_properties.get('instant_fill', True),
            'properties': safe_properties
        }

        super(TradingFactory, self).__init__(**kwargs)
        # Zipline overwrites our portfolio setup, store it for later
        # If has no effect if the user didn't hook the portfolio
        self._saved_portfolio = copy(self.portfolio)

    def hook_portfolio(self, portfolio):
        ''' Replace default zipline portfolio '''
        print('Using custom portfolio: {}'.format(portfolio.__class__))
        self.perf_tracker.cumulative_performance._portfolio_store = \
            portfolio

    @abc.abstractmethod
    def event(self, data):
        ''' User should overwrite this method '''
        pass

    def handle_data(self, data):
        ''' Method called for each event by zipline. In intuition this is the
        place to factorize algorithms and then call event() '''
        if not self.initialized:
            self.perf_tracker.cumulative_performance._portfolio_store = \
                self._saved_portfolio
            self.initialized = True

        # Copied from zipline.algorithm:l225
        if self.history_container:
            self.history_container.update(data, self.datetime)

        try:
            self.event(data)
        except Exception, error:
            # NOTE Temporary debug. Will probably notify the error and go on
            # with signals={}
            raise intuition.errors.AlgorithmEventFailed(
                reason=error, date=self.get_datetime(), data={})

        self._safely_call_middlewares()

    @property
    def _is_live(self):
        ''' Prevent middlewares and orders to work outside live mode '''
        return intuition.utils.is_live(self.get_datetime())

    @property
    def elapsed_time(self):
        return self.get_datetime() - self.portfolio.start_date

    def use(self, func, backtest=False):
        ''' Append a middleware to the algorithm stack '''
        # self.use() is usually called from initialize(), so no logger yet
        print 'registering middleware {}'.format(func.__name__)
        self.middlewares.append({
            'call': func,
            'name': func.__name__,
            'args': func.func_code.co_varnames,
            'allow_backtest': backtest
        })

    def _call_one_middleware(self, middleware):
        ''' Evaluate arguments and execute the middleware function '''
        args = {
            # same as eval() but safer for arbitrary code execution
            arg: reduce(getattr, arg.split('.'), self)
            for arg in middleware['args'] if hasattr(self, arg)
        }
        middleware['call'](**args)

    def _safely_call_middlewares(self):
        ''' Execute the middleware stack '''
        for middleware in self.middlewares:
            name = middleware['name']
            # TODO Call upon datetime conditions
            # Some middlewares send stuff over the wires. This little security
            # prevent us from performing DDOS
            if not self._is_live and not middleware['allow_backtest']:
                self.logger.debug('skipping middleware', name=name)
            else:
                self.logger.debug('calling middleware', name=name)
                self._call_one_middleware(middleware)
