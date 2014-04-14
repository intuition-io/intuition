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
from zipline.algorithm import TradingAlgorithm
from intuition.errors import AlgorithmEventFailed


class TradingFactory(TradingAlgorithm):
    '''
    Intuition surcharge of main zipline class, but fully compatible.  Its role
    is slightly different : the user will eventually expose an event() method
    meant to return buy and sell signals, processed, optionnaly, further by the
    portfolio strategy. However it remains fully compatible with zipline method
    (i.e. it's stil possible to execute orders within the event method and not
    consider any portfolio strategy aside)
    '''

    __metaclass__ = abc.ABCMeta

    # TODO Use another zipline mechanism
    days = 0
    sids = []
    middlewares = []
    auto = False
    manager = None

    def __init__(self, *args, **kwargs):
        self.realworld = kwargs.get('properties', {}).get('realworld')
        TradingAlgorithm.__init__(self, *args, **kwargs)

    def _is_interactive(self):
        ''' Prevent middlewares and orders to work outside live mode '''
        return not (
            self.realworld and (dt.date.today() > self.datetime.date()))

    def use(self, func, when='whenever'):
        ''' Append a middleware to the algorithm '''
        #NOTE A middleware Object ?
        print('registering middleware {}'.format(func.__name__))
        self.middlewares.append({
            'call': func,
            'name': func.__name__,
            'args': func.func_code.co_varnames,
            'when': when})

    #NOTE I'm not superfan of initialize + warm
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
        self.days += 1
        signals = {}
        self.orderbook = {}

        if self.initialized and self.manager:
            self.manager.update(
                self.portfolio,
                self.datetime,
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
            raise AlgorithmEventFailed(
                reason=error, date=self.datetime, data=data)

        # One can process orders within the alogrithm and don't return anything
        if signals and self.manager:
            if (signals.get('buy') or signals.get('sell')):
                self.orderbook = self.manager.trade_signals_handler(signals)
                if self.auto and self._is_interactive():
                    self.process_orders(self.orderbook)

        if self._is_interactive():
            self._call_middlewares()

    def process_orders(self, orderbook):
        ''' Default and costant orders processor. Overwrite it for more
        sophisticated strategies '''
        for stock, alloc in orderbook.iteritems():
            self.logger.info('{}: Ordered {} {} stocks'.format(
                self.datetime, stock, alloc))
            if isinstance(alloc, int):
                self.order(stock, alloc)
            elif isinstance(alloc, float) and \
                    alloc >= -1 and alloc <= 1:
                self.order_percent(stock, alloc)
            else:
                self.logger.warning(
                    '{}: invalid order for {}: {})'
                    .format(self.datetime, stock, alloc))

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

    def _check_condition(self, when):
        ''' Verify that the middleware condition is True '''
        #TODO Use self.datetime to evaluate <when>
        return True

    def _call_middlewares(self):
        ''' Execute the middleware stack '''
        for middleware in self.middlewares:
            if self._check_condition(middleware['when']):
                self._call_one_middleware(middleware)
