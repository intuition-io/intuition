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

    def __init__(self, *args, **kwargs):
        self.data_generator = DataFrameSource
        TradingAlgorithm.__init__(self, *args, **kwargs)

    def go(self, source, sim_params=None, benchmark_return_source=None):
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

    #NOTE I'm not superfan of initialize + preamble
    def preamble(self, data):
        ''' Called at the first handle_data frame '''
        pass

    @abc.abstractmethod
    def event(self, data):
        ''' Users should overwrite this method '''
        pass

    def handle_data(self, data):
        self.day += 1
        signals = {}

        #NOTE Temporary
        #if self.debug:
            #print('\n' + 79 * '=')
            #print self.portfolio
            #print(79 * '=' + '\n')

        if self.initialized:
            user_instruction = self.manager.update(
                self.portfolio,
                self.datetime,
                self.perf_tracker.cumulative_risk_metrics.to_dict())
            self.process_instruction(user_instruction)
        else:
            # Perf_tracker needs at least a turn to have an index
            self.preamble(data)
            self.initialized = True

        signals = self.event(data)

        if signals:
            order_book = self.manager.trade_signals_handler(signals)
            for stock in order_book:
                self.order(stock, order_book[stock])
                if self.debug:
                    self.logger.notice('{}: Ordered {} {} stocks'.format(
                        self.datetime, stock, order_book[stock]))

    def process_instruction(self, instruction):
        '''
        Process orders from instruction
        '''
        if instruction:
            self.logger.info('Processing user instruction')
            if (instruction['command'] == 'order') \
                    and ('amount' in instruction):
                self.logger.error('{}: Ordering {} {} stocks'.format(
                    self.datetime,
                    instruction['amount'],
                    instruction['asset']))

    #NOTE self.done flag could be used to avoid in zipline waist of computation
    #TODO Anyway should find a more elegant way
    def stop_trading(self):
        ''' Convenient method to stop calling user algorithm and just finish
        the simulation'''
        self.logger.info('Trader out of the market')
        #NOTE Selling every open positions ?
        # Saving the portfolio in database, eventually for reuse
        self.db.save_portfolio(self.datetime, self.portfolio)

        # Closing generator
        self.date_sorted.close()
        #self.set_datetime(self.sim_params.last_close)
        self.done = True
