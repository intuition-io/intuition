"""
Tools to generate data sources.
"""
import ipdb as pdb

import sys
import os
import time
import datetime
import pandas as pd

sys.path.append(os.environ['ZIPLINE'])
from zipline.gens.utils import hash_args
from zipline.sources.data_source import DataSource

sys.path.append(os.environ['QTRADE'])
from pyTrade.data.remote import Fetcher

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
        self.sids = kwargs.get('sids', data['tickers'])
        self.start = kwargs.get('start', data['index'][0])
        self.end = kwargs.get('end', data['index'][-1])

        # Hash_value for downstream sorting.
        self.arg_string = hash_args(data, **kwargs)

        self._raw_data = None

        self.remote = Fetcher()

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

    def raw_data_gen(self):
        for dt in self.data['index']:
        #for dt, series in self.data.iterrows():
            '''
            current_dt = datetime.datetime.now()
            while (current_dt.minute != dt.minute) and (current_dt.hour != dt.hour) :
                time.sleep(15)
                current_dt = datetime.datetime.now()
                print('Waiting {} / {}'.format(current_dt, dt))
            '''
            for sid in self.data['tickers']:
            #for sid, price in series.iterkv():
                if sid in self.sids:
                    #TODO Retrieving market and probably symbol informations from database
                    data = self.remote.get_stock_snapshot([sid], ['nasdaq'], light=False)
                    if not data:
                        log.error('** No data snapshot available, maybe stopped by google ?')
                        sys.exit(2)
                    event = {
                        'dt': dt,
                        'sid': sid,
                        'price': float(data[sid]['last']),
                        'currency': data[sid]['currency'],
                        'perc_change': float(data[sid]['perc_change']),
                        'volume': int(data[sid]['volume']),
                    }
                    yield event

    @property
    def raw_data(self):
        if not self._raw_data:
            self._raw_data = self.raw_data_gen()
        return self._raw_data
