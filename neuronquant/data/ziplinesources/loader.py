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


from collections import OrderedDict
from datetime import datetime

from neuronquant.zipline.data.treasuries import get_treasury_data
#from neuronquant.zipline.data.benchmarks import get_benchmark_returns
from neuronquant.zipline.protocol import DailyReturn

import neuronquant.utils.datautils as datautils

from operator import attrgetter

import pytz
import pandas as pd


#TODO A class: the constructor could set from run_backtest the parameters, and only the function will be sent

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

    def load_market_data(self, bm_symbol='^GSPC'):
        #TODO Parametric
        event_dt = datetime.today().replace(tzinfo=pytz.utc)

        # Getting today benchmark return
        #NOTE Seems shit but later, previous days could be used to compute indicators
        #last_bench_return = get_benchmark_returns(bm_symbol, start_date=(event_dt - pd.datetools.Day(self.loopback)))
        #last_bench_return = last_bench_return[-1]
        #print('Benchmark on {}: {}'.format(last_bench_return.date, last_bench_return.returns))

        #TODO More efficient way to navigate in a dit
        for exchange in datautils.Exchange:
            if datautils.Exchange[exchange]['index'] == bm_symbol:
                code = datautils.Exchange[exchange]['code']
                break

        bm_returns = []
        while event_dt < self.last_trading_day:
            #TODO Current value to give
            #TODO Append only if trading day and market hour
            #bm_returns.append(DailyReturn(date=event_dt.replace(microsecond=0), returns=last_bench_return.returns))
            bm_returns.append(DailyReturn(date=event_dt.replace(microsecond=0), returns=code))
            #TODO Frequency control
            event_dt += self.offset

        bm_returns = sorted(bm_returns, key=attrgetter('date'))

        tr_gen = get_treasury_data()
        while True:
            try:
                last_tr = tr_gen.next()
            except StopIteration:
                break

        tr_curves = {}
        tr_dt = datetime.today().replace(tzinfo=pytz.utc)
        while tr_dt < self.last_trading_day:
            #tr_dt = tr_dt.replace(hour=0, minute=0, second=0, tzinfo=pytz.utc)
            tr_curves[tr_dt] = last_tr
            tr_dt += self.offset

        tr_curves = OrderedDict(sorted(
                                ((dt, c) for dt, c in tr_curves.iteritems()),
                                key=lambda t: t[0]))

        return bm_returns, tr_curves
