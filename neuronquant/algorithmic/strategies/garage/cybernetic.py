#
# Copyright 2012 Xavier Bruhiere
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
from zipline.transforms import batch_transform
import pandas
import math


@batch_transform
def get_MinMax(datapanel):
    global Stock1
    prices = datapanel['price']
    prices['Min'] = pandas.stats.moments.rolling_min(prices[Stock1], 20)
    prices['Max'] = pandas.stats.moments.rolling_max(prices[Stock1], 20)
    return prices


#TODO Finish zipline adaptation and integrate it
#https://www.quantopian.com/posts/john-ehlers-fischer-transform?utm_source=All+Active+Members&utm_campaign=9887b9670f-13-04-24-backtested-thurs-send&utm_medium=email
class FischerTransform(TradingAlgorithm):
    def initialize(self, properties):
        self.save = properties.get('save', 0)
        self.debug = properties.get('debug', 0)

        self.extrems_transform = get_MinMax(
                refresh_period=properties.get('refresh_period', 10),
                window_length=properties.get('window_length', 40),
                compute_only_full=False)

        self.qty = 100
        #Stock1 = int(str(self.Stock1)[9:-1])

    def handle_data(self, data):
        import ipdb; ipdb.set_trace()
        result = self.extrems_transform.handle_data(data)
        if result is None:
            return
        min = result['Min'][-1]
        max = result['Max'][-1]
        mid = min + (max - min) / 2

        for sid on data:
            diff = data[sid].price - mid
            transform = (2 * math.exp(diff) - 1) / (2 * math.exp(diff) + 1)
            if transform > 0.9999:
                transform = 1
            elif transform < -0.9999:
                transform = -1
            self.record(Transform=transform)
            self.order_handling(self, data, transform)

    def order_handling(self, data, transform):
        if transform == -1:
            # Are we long or neutral?
            if self.portfolio.positions[self.Stock1].amount >= 0:
                # Close our long position if we have one
                self.close_position(self, data)
            self.order(self.Stock1, -self.qty)
        if transform == 1:
            # Are we short or neutral?
            if self.portfolio.positions[self.Stock1].amount <= 0:
                # Close our short position if we have one
                self.close_position(self, data)
            self.order(self.Stock1, self.qty)
            return

    def close_position(self, result):
        # Open position?
        if self.portfolio.positions[self.Stock1].amount > 0:
            self.order(self.Stock1, -self.qty)
        elif self.portfolio.positions[self.Stock1].amount < 0:
            self.order(self.Stock1, self.qty)
        return
