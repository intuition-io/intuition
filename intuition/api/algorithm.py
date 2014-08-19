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
from intuition.api.middleware import TimeGuard, Middleware


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

    @property
    def elapsed_time(self):
        return self.get_datetime() - self.portfolio.start_date

    @property
    def is_live(self):
        return intuition.utils.is_live(self.get_datetime())

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
                reason=error, date=self.get_datetime(), data={}
            )

        for mdw in self.middlewares:
            self.process_middleware(mdw)

    def use(self, func, when=['every events'], hf=False, critical=False):
        checker = TimeGuard(None, None, when, hf)
        self.middlewares.append(Middleware(func, checker, critical))
        # self.use() is usually called from initialize(), so no logger yet
        print('Registered middleware {}'.format(str(func)))

    def process_middleware(self, mdw):
        if mdw.check(self.get_datetime()):
            requested_attributes = {
                # same as eval() but safer for arbitrary code execution
                arg: reduce(getattr, arg.split('.'), self)
                for arg in mdw.args if hasattr(self, arg)
            }
            result = mdw(**requested_attributes)
            self.logger.debug(
                'processed middleware', name=mdw.name, result=result
            )
