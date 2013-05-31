#
# Copyright 2013 xavier
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


from zipline.algorithm import TradingAlgorithm


class pouet(TradingAlgorithm):
    ''' Template class '''
    def initialize(self, properties):
        self.debug = properties.get('debug', False)
        self.save = properties.get('save', False)
        self.loops = 0

    def handle_data(self, data):
        self.loops += 1
        signals = {}
        ''' ------------------------------------------------------    Init   --'''
        if self.initialized:
            instructions = self.manager.update(
                    self.portfolio,
                    self.datetime.to_pydatetime(),
                    self.perf_tracker.cumulative_risk_metrics.to_dict(),
                    save=self.save,
                    widgets=False)
        else:
            # Perf_tracker need at least a turn to have an index
            self.initialized = True

        ''' --------------------------------------------------    Scan   --'''
        for ticker in data:
            self.logger.debug(data[ticker].price)

        ''' ------------------------------------------------------   Orders  --'''
        if signals:
            orderBook = self.manager.trade_signals_handler(signals)
            for stock in orderBook:
                if self.debug:
                    self.logger.notice('{}: Ordering {} {} stocks'.format(
                        self.datetime, stock, orderBook[stock]))