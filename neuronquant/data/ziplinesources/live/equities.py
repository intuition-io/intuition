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
import sys
import time
import pytz
import datetime
import pandas as pd

from zipline.gens.utils import hash_args
from zipline.sources.data_source import DataSource

from neuronquant.tmpdata.remote import Remote
from neuronquant.data.datafeed import DataFeed

import logbook
log = logbook.Logger('DataLiveSource')


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
        self.sids  = kwargs.get('sids', data['tickers'])
        self.start = kwargs.get('start', data['index'][0])
        self.end   = kwargs.get('end', data['index'][-1])

        #self.fake_index = pd.date_range(self.start, self.end, freq=pd.datetools.BDay())

        # Hash_value for downstream sorting.
        self.arg_string = hash_args(data, **kwargs)

        self._raw_data = None

        self.remote = Remote()
        self.feed = DataFeed()

    @property
    def mapping(self):
        return {
            'dt': (lambda x: x, 'dt'),
            'sid': (lambda x: x, 'sid'),
            'price': (float, 'price'),
            'currency': (str, 'currency'),
            'perc_change': (float, 'perc_change'),
            'volume': (int, 'volume'),
        }

    @property
    def instance_hash(self):
        return self.arg_string

    def _wait_for_dt(self, dt):
        '''
        Only return when we reach given datetime
        '''
        # QuanTrade works with utc dates, conversion
        # are made for I/O
        #while datetime.datetime.now(pytz.utc) < dt:
        now = datetime.datetime.now(pytz.utc)
        while now < dt:
            log.debug('Waiting for {} / {}'.format(now, dt))
            time.sleep(15)
            now = datetime.datetime.now(pytz.utc)

    def _get_updated_index(self):
        '''
        truncate past dates in index
        '''
        late_index = self.data['index']
        current_dt = datetime.datetime.now(pytz.utc)
        selector = (late_index.day > current_dt.day) \
                | ((late_index.day == current_dt.day) & (late_index.hour > current_dt.hour)) \
                | ((late_index.day == current_dt.day) & (late_index.hour == current_dt.hour) & (late_index.minute >= current_dt.minute))
        return self.data['index'][selector]

    def raw_data_gen(self):
        index = self._get_updated_index()
        for dt in index:
            self._wait_for_dt(dt)
            snapshot = self.remote.fetch_equities_snapshot(symbols=self.sids, level=2)
            if snapshot.empty:
                log.error('** No data snapshot available, maybe stopped by google ?')
                sys.exit(2)
            for sid in self.sids:
                # Fix volume = 0, (later will be denominator)
                if not int(snapshot[sid]['volume']):
                    #TODO Here just a special value that the algo could detect like a missing data
                    snapshot[sid]['volume'] = 10001
                #import ipdb; ipdb.set_trace()
                #NOTE Conversions here are useless ?
                if snapshot[sid]['perc_change'] == '':
                    snapshot[sid]['perc_change'] = 0
                event = {
                    'dt': dt,
                    'sid': sid,
                    'price': float(snapshot[sid]['last']),
                    'currency': snapshot[sid]['currency'],
                    'perc_change': float(snapshot[sid]['perc_change']),
                    'volume': int(snapshot[sid]['volume']),
                }
                yield event

    @property
    def raw_data(self):
        if not self._raw_data:
            self._raw_data = self.raw_data_gen()
        return self._raw_data
