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
import datetime as dt
import zipline.algorithm
import intuition.errors


# pylint: disable=R0921
class TradingFactory(zipline.algorithm.TradingAlgorithm):
    '''
    Intuition surcharge of main zipline class, but fully compatible.  Its role
    is slightly different : the user will eventually expose an event() method
    meant to return buy and sell signals, processed, optionnaly, further by the
    portfolio strategy. However it remains fully compatible with zipline method
    (i.e. it's stil possible to execute orders within the event method and not
    consider any portfolio strategy aside)
    '''

    __metaclass__ = abc.ABCMeta

    def __init__(self, identity='johndoe', properties=None):
        # Attributes initialization
        self.sids = []
        self.middlewares = []
        self.auto = False
        self.manager = None
        self.initialized = False
        self.orderbook = {}

        # User customized attributes
        safe_properties = properties or {}
        self.identity = identity
        self.realworld = safe_properties.get('realworld')
        zipline.algorithm.TradingAlgorithm.__init__(
            self, properties=safe_properties)

    def _is_interactive(self):
        ''' Prevent middlewares and orders to work outside live mode '''
        return not (self.realworld and
                    dt.date.today() > self.datetime.date())

    def use(self, func):
        ''' Append a middleware to the algorithm '''
        # NOTE A middleware Object ?
        # self.use() is usually called from initialize(), so no logger yet
        print 'registering middleware {}'.format(func.__name__)
        self.middlewares.append({
            'call': func,
            'name': func.__name__,
            'args': func.func_code.co_varnames
        })

    # NOTE I'm not superfan of initialize + warm
    def warm(self, data):
        ''' Called at the first handle_data frame '''
        pass

    @abc.abstractmethod
    def event(self, data):
        ''' User should overwrite this method '''
        pass

    def handle_data(self, data):
        ''' Method called for each event by zipline. In intuition this is the
        place to factorize algorithms and then call event() '''
        signals = {}
        self.orderbook = {}

        # Everytime but the first tick
        if self.initialized and self.manager:
            # Keep the portfolio aware of the situation
            self.manager.update(
                self.portfolio,
                self.get_datetime(),
                self.perf_tracker.cumulative_risk_metrics.to_dict())
        else:
            # Perf_tracker needs at least a turn to have an index
            self.sids = data.keys()
            self.warm(data)
            self.initialized = True
            return

        try:
            signals = self.event(data)
        except Exception, error:
            # NOTE Temporary debug. Will probably notify the error and go on
            # with signals={}
            raise intuition.errors.AlgorithmEventFailed(
                reason=error, date=self.get_datetime(), data=data)

        # One can process orders within the alogrithm and don't return anything
        if signals and self.manager:
            if signals.get('buy') or signals.get('sell'):
                self.orderbook = self.manager.trade_signals_handler(signals)
                if self.auto and self._is_interactive():
                    self.process_orders(self.orderbook)

        # Some middlewares send stuff over the wires. This little security
        # prevent us from performing a DDOS
        if self._is_interactive():
            self._call_middlewares()

    def process_orders(self, orderbook):
        ''' Default and costant orders processor. Overwrite it for more
        sophisticated strategies '''
        for stock, alloc in orderbook.iteritems():
            self.logger.info('{}: Ordered {} {} stocks'.format(
                self.get_datetime(), stock, alloc))
            if isinstance(alloc, int):
                self.order(stock, alloc)
            elif isinstance(alloc, float) and \
                    alloc >= -1 and alloc <= 1:
                self.order_percent(stock, alloc)
            else:
                self.logger.warning(
                    '{}: invalid order for {}: {})'
                    .format(self.datetime, stock, alloc))

    @property
    def elapsed_time(self):
        return self.get_datetime() - self.portfolio.start_date

    def _call_one_middleware(self, middleware):
        ''' Evaluate arguments and execute the middleware function '''
        args = {}
        for arg in middleware['args']:
            if hasattr(self, arg):
                # same as eval() but safer for arbitrary code execution
                args[arg] = reduce(getattr, arg.split('.'), self)
        self.logger.debug('calling middleware event {}'
                          .format(middleware['name']))
        middleware['call'](**args)

    def _call_middlewares(self):
        ''' Execute the middleware stack '''
        for middleware in self.middlewares:
            # TODO Call upon datetime conditions
            self._call_one_middleware(middleware)
