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


import pandas as pd
import time
import pytz
import datetime

from zipline.sources.data_source import DataSource
from zipline.gens.utils import hash_args


#TODO Mapping and raw_data_gen could be generic and set here
class DataFactory(DataSource):
    '''
    Intuition surcharge of DataSource zipline class

    Configuration options:

    sids   : list of values representing simulated internal sids
    start  : start date
    delta  : timedelta between internal events
    filter : filter to remove the sids
    '''
    def __init__(self, data_descriptor, **kwargs):
        assert isinstance(data_descriptor['index'],
                          pd.tseries.index.DatetimeIndex)

        #self.data_descriptor = data_descriptor
        # Unpack config dictionary with default values.
        self.sids = kwargs.get('sids', data_descriptor['tickers'])
        self.start = kwargs.get('start', data_descriptor['index'][0])
        self.end = kwargs.get('end', data_descriptor['index'][-1])
        self.index = data_descriptor['index']

        # Hash_value for downstream sorting.
        self.arg_string = hash_args(data_descriptor, **kwargs)

        # Check provided informations
        assert isinstance(self.sids, list)

        self._raw_data = None

    @property
    def instance_hash(self):
        return self.arg_string

    @property
    def raw_data(self):
        if not self._raw_data:
            self._raw_data = self.raw_data_gen()
        return self._raw_data

    def get_data(self):
        ''' This method must be over written by the user custom data source '''
        return pd.DataFrame()

    def build_event(self, dt, sid, series):
        event = {
            'dt': dt,
            'sid': sid}
        if isinstance(series, pd.Series):
            if sid in series.keys():
                event.update({'price': series[sid],
                              'volume': 1000})
            else:
                event.update(series.to_dict())
        elif isinstance(series, pd.Dataframe):
            event.update(series[sid].to_dict())

        return event

    def raw_data_gen(self):
        self.data = self.get_data()

        if isinstance(self.data, pd.DataFrame):
            for sid in self.sids:
                for dt, series in self.data.iterrows():
                    yield self.build_event(dt, sid, series)

        elif isinstance(self.data, pd.Panel):
            for sid, df in self.data.iteritems():
                for dt, series in df.iterrows():
                    yield self.build_event(dt, sid, series)

        else:
            raise TypeError("Invalid data source type")

    # ========================== Live oriented funcitons ===== #
    def _wait_for_dt(self, dt):
        '''
        Only return when we reach given datetime
        '''
        # QuanTrade works with utc dates, conversion
        # are made for I/O
        now = datetime.datetime.now(pytz.utc)
        while now < dt:
            print('Waiting for {} / {}'.format(now, dt))
            time.sleep(15)
            now = datetime.datetime.now(pytz.utc)

    def _get_updated_index(self):
        '''
        truncate past dates in index
        '''
        late_index = self.data['index']
        current_dt = datetime.datetime.now(pytz.utc)
        selector = (late_index.day > current_dt.day) \
            | ((late_index.day == current_dt.day)
                & (late_index.hour > current_dt.hour)) \
            | ((late_index.day == current_dt.day)
                & (late_index.hour == current_dt.hour)
                & (late_index.minute >= current_dt.minute))
        return self.data['index'][selector]
