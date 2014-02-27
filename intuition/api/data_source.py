# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Intuition Data source api
  -------------------------

  Trading data source factory. Everything that can extend in a useful way
  zipline.DataSource goes here. Future data sources should inherit from
  this class.

  :copyright (c) 2014 Xavier Bruhiere
  :license: Apache 2.0, see LICENSE for more details.
'''


import abc
import pandas as pd
from zipline.sources.data_source import DataSource
from zipline.gens.utils import hash_args
import dna.logging
import intuition.utils as utils
from intuition.data.utils import smart_selector
from intuition.errors import LoadDataFailed


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


class HybridDataFactory(DataSource):
    '''
    Surcharge of zipline.DataSource, switching automatically between live
    stream and backtest sources

    Configuration options:

    sids   : list of values representing simulated internal sids
             It can be an explicit list of symbols, or a universe like nyse,20
             (that will pick up 20 random symbols from nyse exchange)
    start  : start date
    delta  : timedelta between internal events
    filter : filter to remove the sids
    '''

    __metaclass__ = abc.ABCMeta

    backtest = None
    live = None
    switched = False
    wait_interval = 15

    def __init__(self, data_descriptor, **kwargs):
        assert isinstance(data_descriptor['index'],
                          pd.tseries.index.DatetimeIndex)

        self.log = dna.logging.logger(__name__)

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

        if hasattr(self.backtest, 'mapping'):
            self.current_mapping = self.backtest.mapping
        else:
            self.current_mapping = self.mapping

    @property
    def mapping(self):
        return {
            'dt': (lambda x: x, 'dt'),
            'sid': (lambda x: x, 'sid'),
            'price': (float, 'price'),
            'volume': (int, 'volume'),
        }

    @abc.abstractmethod
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
    def backtest_data(self):
        ''' Users should overwrite this method '''
        pass

    @abc.abstractmethod
    def live_data(self):
        ''' Users should overwrite this method '''
        pass

    def _switch_context(self):
        self.log.info(
            'switching from backtest to live mode')
        self.switched = True
        if self.live:
            if hasattr(self.live, 'mapping'):
                self.current_mapping = self.live.mapping

    def apply_mapping(self, raw_row):
        row = {target: mapping_func(raw_row[source_key])
               for target, (mapping_func, source_key)
               in self.current_mapping.items()}
        row.update({'source_id': self.get_hash()})
        row.update({'type': self.event_type})
        return row

    def raw_data_gen(self):
        if self.backtest:
            try:
                bt_data = self.backtest_data()
            except Exception as error:
                raise LoadDataFailed(sids=self.sids, reason=error)
        else:
            bt_data = None

        for date in self.index:
            self.log.debug('--> next tick {}'.format(date))
            is_live = utils.next_tick(date)
            if not is_live:
                date = date.replace(hour=0)

                if isinstance(bt_data, pd.DataFrame):
                    if date not in bt_data.index:
                        continue
                    for sid in self.sids:
                        series = bt_data.ix[date]
                        yield _build_event(date, sid, series)
                elif isinstance(bt_data, pd.Panel):
                    df = self.data.major_xs(date)
                    for sid, series in df.iterkv():
                        yield _build_event(date, sid, series)
            else:
                if not self.switched:
                    self._switch_context()
                try:
                    snapshot = self.live_data()
                except Exception as error:
                    raise LoadDataFailed(sids=self.sids, reason=error)
                for sid, series in snapshot.iterkv():
                    yield _build_event(date, sid, series)
