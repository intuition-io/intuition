#
# Copyright 2013 Quantopian, Inc.
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


# Benchmark loader modified to allow live data streaming


from datetime import datetime
import pandas as pd
from collections import OrderedDict

import zipline.data.loader as zipline

import intuition.data.utils as datautils


class LiveBenchmark(object):
    def __init__(self, end, frequency='daily', loopback=4):
        self.last_trading_day = end
        self.loopback = loopback
        if frequency == 'minute':
            self.offset = pd.datetools.Minute()
        elif frequency == 'daily':
            self.offset = pd.datetools.Day()
        else:
            raise NotImplementedError()

    def normalize_date(self, test_date):
        ''' Same function as zipline.finance.trading.py'''
        test_date = pd.Timestamp(test_date, tz='UTC')
        return pd.tseries.tools.normalize_date(test_date)

    def surcharge_market_data(self, bm_symbol='^GSPC'):
        #TODO Parametric
        #event_dt = datetime.today().replace(tzinfo=pytz.utc)
        event_dt = self.normalize_date(datetime.now())

        #TODO Handle invalid code
        for exchange, infos in datautils.Exchanges.iteritems():
            if infos['symbol'] == bm_symbol:
                code = datautils.Exchanges[exchange]['code']
                break

        bm_returns, tr_curves = zipline.load_market_data(bm_symbol)

        dates = pd.date_range(event_dt,
                              periods=len(bm_returns))
        #NOTE What is tr_curves['tid'] ?
        #TODO Replace values to detect the fake later
        tr_fake = OrderedDict(sorted(
            ((pd.Timestamp(event_dt + i*self.offset), c)
             for i, c in enumerate(tr_curves.values())),
            key=lambda t: t[0]))

        bm_fake = pd.Series([code] * len(dates), index=dates)
        for i, dt in enumerate(tr_curves.keys()):
            pd.Timestamp(event_dt + i * self.offset)

        return bm_fake, tr_fake
