# -*- coding: utf-8 -*-
# vim:fenc=utf-8
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


import abc

from zipline.algorithm import TradingAlgorithm
from zipline.sources import DataFrameSource


class TradingFactory(TradingAlgorithm):
    '''
    Intuition surcharge of main zipline class.
    Its role is slightly different : the user will eventually expose an event()
    method meant to return buy and sell signals, processed further by the
    portfolio strategy. However it remains fully compatible with zipline method
    (i.e. it's stil possible to execute orders within the event method and not
    consider any portfolio strategy aside)
    '''

    __metaclass__ = abc.ABCMeta

    #TODO Use another zipline mechanism
    day = 0
    sids = []
    middlewares = []
    orderbook = {}
    auto = False

    def __init__(self, *args, **kwargs):
        self.data_generator = DataFrameSource
        TradingAlgorithm.__init__(self, *args, **kwargs)

    def use(self, func, when='whenever'):
        ''' Append a middleware to the algorithm '''
        #NOTE A middleware Object ?
        print('registering middleware {}'.format(func.__name__))
        self.middlewares.append({
            'call': func,
            'name': func.__name__,
            'args': func.func_code.co_varnames,
            'when': when})

    def trade(self, source, sim_params=None):
        if isinstance(source, dict):
            source = self.data_generator(source)

        return self.run(source, sim_params)

    #TODO How can I use several sources ?
    def set_data_generator(self, generator_class):
        ''' Register a data source to the algorithm '''
        self.data_generator = generator_class

    #NOTE I'm not superfan of initialize + warming
    def warming(self, data):
        ''' Called at the first handle_data frame '''
        pass

    @abc.abstractmethod
    def event(self, data):
        ''' Users should overwrite this method '''
        pass

    def handle_data(self, data):
        ''' Method called for each event by zipline. In intuition this is the
        place to factorize algorithms and then call event() '''
        self.day += 1
        signals = {}
        self.orderbook = {}

        if self.initialized and self.manager:
            self.manager.update(
                self.portfolio,
                self.datetime,
                self.perf_tracker.cumulative_risk_metrics.to_dict())
        else:
            # Perf_tracker needs at least a turn to have an index
            self.warming(data)
            self.initialized = True
            self.sids = data.keys()

        signals = self.event(data)

        if signals and self.manager:
            self.orderbook = self.manager.trade_signals_handler(signals)
            if self.auto:
                self.process_orders(self.orderbook)

        self._call_middlewares()

    def process_orders(self, orderbook):
        ''' Default and costant orders processor. Overwrite it for more
        sophistiated strategies '''
        for stock in orderbook:
            self.order(stock, orderbook[stock])
            self.logger.debug('{}: Ordered {} {} stocks'.format(
                self.datetime, stock, orderbook[stock]))

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
