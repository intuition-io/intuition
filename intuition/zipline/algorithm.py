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
#
# -*- coding: utf-8 -*-
# vim:fenc=utf-8


import abc

from zipline.algorithm import TradingAlgorithm
from zipline.sources import DataFrameSource
#from zipline.protocol import Event
#import zipline.protocol


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

    is_live = False
    debug = False
    #TODO Use another zipline mechanism
    day = 0
    middlewares = []

    def __init__(self, *args, **kwargs):
        self.data_generator = DataFrameSource
        TradingAlgorithm.__init__(self, *args, **kwargs)

    def use(self, func, when='whatever'):
        self.middlewares.append({
            'call': func,
            'name': func.__name__,
            'args': func.func_code.co_varnames,
            'when': when})

    def go(self, source, sim_params=None):
        '''
        if self.is_live:
            benchmark_return_source = [
                Event({'dt': dt,
                       'returns': 0.0,
                       'type': zipline.protocol.DATASOURCE_TYPE.BENCHMARK,
                       'source_id': 'benchmarks'})
                for dt in source['index']
                if dt.date() >= sim_params.period_start.date()
                and dt.date() <= sim_params.period_end.date()]
          '''

        if isinstance(source, dict):
            source = self.data_generator(source)

        #return self.run(source, sim_params, benchmark_return_source)
        # 0.5.9 compatibility
        return self.run(source, sim_params)

    def set_data_generator(self, generator_class):
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
        self.day += 1
        signals = {}

        if self.initialized:
            self.manager.update(
                self.portfolio,
                self.datetime,
                self.perf_tracker.cumulative_risk_metrics.to_dict())
        else:
            # Perf_tracker needs at least a turn to have an index
            self.warming(data)
            self.initialized = True

        signals = self.event(data)

        self._call_middlewares()

        if signals:
            order_book = self.manager.trade_signals_handler(signals)
            self.process_orders(order_book)

    def process_orders(self, order_book):
        for stock in order_book:
            self.order(stock, order_book[stock])
            if self.debug:
                self.logger.notice('{}: Ordered {} {} stocks'.format(
                    self.datetime, stock, order_book[stock]))

    def _call_one_middleware(self, mw):
        args = {}
        for arg in mw['args']:
            if hasattr(self, arg):
                args[arg] = eval('self.' + arg)
        self.logger.info('calling middleware event {}'
                         .format(mw['name']))
        mw['call'](**args)

    def _call_middlewares(self):
        for mw in self.middlewares:
            #TODO Use the <when> keyword
            self._call_one_middleware(mw)
