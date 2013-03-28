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


"""
Tools to generate data sources.
"""
import time
import datetime
import pandas as pd

from zipline.gens.utils import hash_args
from zipline.sources.data_source import DataSource

from neuronquant.data.forex import ConnectTrueFX

import logbook
log = logbook.Logger('ForexLiveSource')


class DataLiveSource(DataSource):
    """
    Yields all events in event_list that match the given sid_filter.
    If no event_list is specified, generates an internal stream of events
    to filter.  Returns all events if filter is None.

    Configuration options:

    sids   : list of values representing simulated internal sids
    start  : start date
    delta  : timedelta between internal events
    filter : filter to remove the sids
    """

    def __init__(self, data, **kwargs):
        assert isinstance(data['index'], pd.tseries.index.DatetimeIndex)

        self.data = data
        # Unpack config dictionary with default values.
        #NOTE Can apply a filter with sids, used while iterating on it later
        self.sids  = kwargs.get('sids', data['tickers'])
        self.start = kwargs.get('start', data['index'][0])
        self.end   = kwargs.get('end', data['index'][-1])

        #self.fake_index = pd.date_range(self.start, self.end, freq=pd.datetools.Minute())

        # Hash_value for downstream sorting.
        self.arg_string = hash_args(data, **kwargs)

        self._raw_data = kwargs.pop('data_gen') if 'data_gen' in kwargs else None
        #self._raw_data = None

        assert isinstance(self.sids, list)
        self.forex = ConnectTrueFX(pairs=self.sids)

    @property
    def mapping(self):
        return {
            'dt': (lambda x: x, 'dt'),
            #TODO Here conversion (weird result for now)
            #'trade_time': (lambda x: pd.tslib.i8_to_pydt(x + '000000'), 'trade_time'),
            'trade_time': (lambda x: pd.datetime.utcfromtimestamp(float(x[:-3])), 'trade_time'),
            'sid': (lambda x: x, 'sid'),
            'price': (float, 'bid'),
            'ask': (float, 'ask'),
            'high': (float, 'high'),
            'low': (float, 'low'),
            'volume': (int, 'volume')
        }

    def _wait_for_dt(self, dt):
        '''
        Only return when we reach given datetime
        '''
        current_dt = datetime.datetime.now()
        while (current_dt.minute < dt.minute) or (current_dt.hour < dt.hour) :
            time.sleep(15)
            current_dt = datetime.datetime.now()
            log.info('Waiting {} / {}'.format(current_dt, dt))

    def _get_updated_index(self):
        '''
        truncate past dates in index
        '''
        late_index = self.data['index']
        current_dt = datetime.datetime.now()
        selector = (late_index.day > current_dt.day) \
                | ((late_index.day == current_dt.day) & (late_index.hour > current_dt.hour)) \
                | ((late_index.day == current_dt.day) & (late_index.hour == current_dt.hour) & (late_index.minute >= current_dt.minute))
        return self.data['index'][selector]

    @property
    def instance_hash(self):
        return self.arg_string

    def raw_data_gen(self):
        index = self._get_updated_index()
        #for fake_dt in self.fake_index:
        for dt in index:
            self._wait_for_dt(dt)
            while True:
                log.debug('Waiting for Forex update')
                currencies = self.forex.QueryTrueFX()
                #if not currencies.empty:
                if len(currencies.keys()) >= len(self.sids):
                    log.debug('New income data, fire an event !')
                    break
                time.sleep(30)

            try:
                for sid in self.sids:
                    assert sid in currencies.columns
                    log.debug('Data available:\n{}'.format(currencies[sid]))
                    event = {
                        'dt': dt,
                        'trade_time': currencies[sid]['TimeStamp'],
                        'sid': sid,
                        'bid': currencies[sid]['Bid.Price'],
                        'ask': currencies[sid]['Ask.Price'],
                        'high': currencies[sid]['High'],
                        'low': currencies[sid]['Low'],
                        #'price': currencies[sid]['Bid.Price'],
                        'volume': 10000
                    }
                    yield event
            except:
                import ipdb; ipdb.set_trace()

    @property
    def raw_data(self):
        if not self._raw_data:
            self._raw_data = self.raw_data_gen()
        return self._raw_data
