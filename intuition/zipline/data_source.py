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


import time
import pytz
import datetime
import abc
import sys
import pandas as pd

from zipline.sources.data_source import DataSource
from zipline.gens.utils import hash_args

from intuition.data.utils import smart_selector


def _build_event(date, sid, series):
    ''' Format the input to a zipline compliant event '''
    event = {
        'dt': date,
        'sid': sid}
    if isinstance(series, pd.Series):
        if sid in series.keys():
            event.update({'price': series[sid],
                          'volume': 1000})
        else:
            event.update(series.to_dict())
    elif isinstance(series, pd.DataFrame):
        event.update(series[sid].to_dict())

    return event


class DataFactory(DataSource):
    '''
    Intuition surcharge of DataSource zipline class

    Configuration options:

    sids   : list of values representing simulated internal sids
             It can be an explicit list of symbols, or a universe like nyse,20
             (that will pick up 20 random symbols from nyse exchange)
    start  : start date
    delta  : timedelta between internal events
    filter : filter to remove the sids
    '''

    __metaclass__ = abc.ABCMeta

    def __init__(self, data_descriptor, **kwargs):
        assert isinstance(data_descriptor['index'],
                          pd.tseries.index.DatetimeIndex)

        #self.data_descriptor = data_descriptor
        # Unpack config dictionary with default values.
        self.sids = smart_selector(
            kwargs.get('sids', data_descriptor['universe']))
        self.start = kwargs.get('start', data_descriptor['index'][0])
        self.end = kwargs.get('end', data_descriptor['index'][-1])
        self.index = data_descriptor['index']

        # Hash_value for downstream sorting.
        self.arg_string = hash_args(data_descriptor, **kwargs)

        # Check provided informations
        assert isinstance(self.sids, list)

        self._raw_data = None
        self.initialize(data_descriptor, **kwargs)

    def initialize(self, data_descriptor, **kwargs):
        ''' Abstract method for user custom initialization'''
        pass

    @property
    def instance_hash(self):
        return self.arg_string

    @property
    def raw_data(self):
        if not self._raw_data:
            self._raw_data = self.raw_data_gen()
        return self._raw_data

    @abc.abstractmethod
    def get_data(self):
        ''' Users should overwrite this method '''
        pass

    def raw_data_gen(self):
        try:
            self.data = self.get_data()
        except Exception as e:
            #TODO Identify the error and retry ?
            print self.sids
            sys.exit(e)

        if isinstance(self.data, pd.DataFrame):
            for date, series in self.data.iterrows():
                for sid in self.sids:
                    yield _build_event(date, sid, series)

        elif isinstance(self.data, pd.Panel):
            for date in self.data.major_axis:
                df = self.data.major_xs(date)
                for sid, series in df.iterkv():
                    yield _build_event(date, sid, series)

        else:
            raise TypeError("Invalid data source type")


class LiveDataFactory(DataFactory):
    '''
    Surcharge of DataFactory for live stream sources
    '''

    __metaclass__ = abc.ABCMeta

    wait_interval = 15

    def _wait_for_dt(self, date):
        '''
        Only return when we reach given datetime
        '''
        # Intuition works with utc dates, conversion
        # are made for I/O
        now = datetime.datetime.now(pytz.utc)
        while now < date:
            print('Waiting for {} / {}'.format(now, date))
            time.sleep(self.wait_interval)
            now = datetime.datetime.now(pytz.utc)

    def _get_updated_index(self):
        '''
        truncate past dates in index
        '''
        late_index = self.index
        current_dt = datetime.datetime.now(pytz.utc)
        selector = (late_index.day > current_dt.day) \
            | ((late_index.day == current_dt.day)
                & (late_index.hour > current_dt.hour)) \
            | ((late_index.day == current_dt.day)
                & (late_index.hour == current_dt.hour)
                & (late_index.minute >= current_dt.minute))

        return self.index[selector]

    def raw_data_gen(self):
        index = self._get_updated_index()
        for date in index:
            self._wait_for_dt(date)
            try:
                snapshot = self.get_data()
            except Exception as e:
                print e
                continue

            for sid, series in snapshot.iterkv():
                yield _build_event(date, sid, series)
