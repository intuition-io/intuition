
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

"""
Tools to generate data sources.
"""
import pandas as pd

from neuronquant.tmpdata.remote import Remote

from zipline.gens.utils import hash_args
from zipline.sources.data_source import DataSource


class YahooPriceSource(DataSource):
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

    def __init__(self, data_descriptor, **kwargs):
        assert isinstance(data_descriptor['index'], pd.tseries.index.DatetimeIndex)

        self.data_descriptor = data_descriptor
        # Unpack config dictionary with default values.
        self.sids = kwargs.get('sids', data_descriptor['tickers'])
        self.start = kwargs.get('start', data_descriptor['index'][0])
        self.end = kwargs.get('end', data_descriptor['index'][-1])

        # Hash_value for downstream sorting.
        self.arg_string = hash_args(data_descriptor, **kwargs)

        self._raw_data = None

        self.remote = Remote()

    @property
    def mapping(self):
        return {
            'dt': (lambda x: x, 'dt'),
            'sid': (lambda x: x, 'sid'),
            'price': (float, 'price'),
            'volume': (int, 'volume'),
        }

    @property
    def instance_hash(self):
        return self.arg_string

    def _get(self):
        return self.remote.fetch_equities_daily(self.sids,
            indexes={}, start=self.start, end=self.end)

    def raw_data_gen(self):
        self.data = self._get()
        for dt, series in self.data.iterrows():
            for sid, price in series.iterkv():
                if sid in self.sids:
                    event = {
                        'dt': dt,
                        'sid': sid,
                        'price': price,
                        'volume': 1000,
                    }
                    yield event

    @property
    def raw_data(self):
        if not self._raw_data:
            self._raw_data = self.raw_data_gen()
        return self._raw_data


class YahooOHLCSource(DataSource):
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

    def __init__(self, data_descriptor, **kwargs):
        #assert isinstance(data.major_axis, pd.tseries.index.DatetimeIndex)

        self.data_descriptor = data_descriptor
        # Unpack config dictionary with default values.
        self.sids = kwargs.get('sids', data_descriptor['tickers'])
        self.start = kwargs.get('start', data_descriptor['index'][0])
        self.end = kwargs.get('end', data_descriptor['index'][-1])

        # Hash_value for downstream sorting.
        self.arg_string = hash_args(data_descriptor, **kwargs)

        self._raw_data = None

        self.remote = Remote()

    @property
    def mapping(self):
        mapping = {
            'dt': (lambda x: x, 'dt'),
            'sid': (lambda x: x, 'sid'),
            'price': (float, 'price'),
            'volume': (int, 'volume'),
        }

        # Add additional fields.
        for field_name in self.data.minor_axis:
            if field_name in ['price', 'volume', 'dt', 'sid']:
                continue
            mapping[field_name] = (lambda x: x, field_name)

        return mapping

    @property
    def instance_hash(self):
        return self.arg_string

    def _get(self):
        return self.remote.fetch_equities_daily(self.sids, ohlc=True,
            indexes={}, start=self.start, end=self.end)

    def raw_data_gen(self):
        self.data = self._get()
        import ipdb; ipdb.set_trace()
        for dt in self.data.major_axis:
            df = self.data.major_xs(dt)
            for sid, series in df.iterkv():
                if sid in self.sids:
                    event = {
                        'dt': dt,
                        'sid': sid,
                    }
                    for field_name, value in series.iteritems():
                        event[field_name] = value

                    yield event

    @property
    def raw_data(self):
        if not self._raw_data:
            self._raw_data = self.raw_data_gen()
        return self._raw_data
