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
import pandas


# https://www.quantopian.com/posts/bollinger-bands-with-trading
#NOTE The post_func customs traditionnal data format, interesting
class BollingerBands(TradingAlgorithm):
    def process_df(self, df):
        df = df.rename(columns={'Close': 'price'})
        df = df.fillna(method='ffill')
        df['MA20']     = pandas.stats.moments.rolling_mean(df['price'], 20)
        df['ABS']      = abs(df['price'] - df['MA20'])
        df['STDDEV']   = pandas.stats.moments.rolling_std(df['ABS'], 20)
        df['UPPER_BB'] = df['MA20'] + 2 * df['STDDEV']
        df['LOWER_BB'] = df['MA20'] - 2 * df['STDDEV']
        return df

    def initialize(self, properties):
        #fetch_csv('https://raw.github.com/pcawthron/StockData/master/CMG%202011%20Daily%20Close.csv',
            #date_column='Date',
            #symbol=stock,
            #usecols=['Close'],
            #post_func = self.process_df,
            #date_format='%d/%m/%Y'
            #)
        self.qty = properties.get('quantity', 400)
        self.stddev_limit = properties.get('stddev_limit', 1.75)

    def handle_data(self, data):
        self.manager.update(self.portfolio, self.datetime.to_pydatetime(), save=False)
        for stock in data:
            if str(data[stock].datetime.year) == "2011":
                self.record(CMG=data[stock].price)
                self.record(Upper=data[stock]['UPPER_BB'])
                self.record(MA20=data[stock]['MA20'])
                self.record(Lower=data[stock]['LOWER_BB'])
                self.order_handling(self, data)

    def order_handling(self, data):
        for stock in data:
            # At top of bands?
            if data[stock].price > data[stock]['MA20'] + data[stock]['STDDEV'] * self.stddev_limit :
                # Are we long or neutral?
                if self.portfolio.positions[stock].amount >= 0:
                    # Close our long position if we have one
                    self.close_position(self, data)
                    self.order(stock, -self.qty)

            # At bottom of bands?
            if data[stock].price < data[stock]['MA20'] - data[stock]['STDDEV'] * self.stddev_limit :
                # Are we short or neutral?
                if self.portfolio.positions[stock].amount <= 0:
                    # Close our short position if we have one
                    self.close_position(self, data)
                    self.order(stock, self.qty)
                return

    def close_position(self, data):
        # Open position?
        for stock in data:
            if self.portfolio.positions[stock].amount > 0:
                self.order(stock, -self.qty)
            elif self.portfolio.positions[stock].amount < 0:
                self.order(stock, self.qty)
        return
