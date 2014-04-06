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


#import abc
import pandas as pd
import dna.logging
from zipline.sources.data_source import DataSource
from zipline.gens.utils import hash_args
import intuition.utils as utils
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
    '''

    backtest = None
    live = None
    _is_live = False

    def __init__(self, **kwargs):
        self.log = dna.logging.logger(__name__)

        assert isinstance(kwargs.get('index'),
                          pd.tseries.index.DatetimeIndex)

        # Unpack config dictionary with default values.
        self.sids = kwargs.get('sids') or kwargs.get('universe').sids
        self.start = kwargs.get('start', kwargs['index'][0])
        self.end = kwargs.get('end', kwargs['index'][-1])
        self.index = kwargs['index']

        # Hash_value for downstream sorting.
        self.arg_string = hash_args(**kwargs)
        self._raw_data = None
        # TODO Fails if the class as no get_data method
        if 'backtest' in kwargs:
            self.backtest = kwargs['backtest'](self.sids, kwargs)
        if 'live' in kwargs:
            self.live = kwargs['live'](self.sids, kwargs)

    @property
    def mapping(self):
        if self._is_live:
            return self.live.mapping
        else:
            return self.backtest.mapping

    def raw_data_gen(self):
        # The first date is usually a few seconds before now,
        # so we compare to the next one
        if self.backtest and not utils.is_live(self.index[1]):
            try:
                bt_data = self.backtest.get_data(
                    self.sids, self.start, self.end)
            except Exception as error:
                raise LoadDataFailed(sids=self.sids, reason=error)
        else:
            bt_data = None

        for date in self.index:
            self.log.debug('--> next tick {}'.format(date))
            self._is_live = utils.next_tick(date)
            if not self._is_live:
                date = date.replace(hour=0)
                if isinstance(bt_data, pd.DataFrame):
                    if date not in bt_data.index:
                        continue
                    for sid in self.sids:
                        series = bt_data.ix[date]
                        yield _build_event(date, sid, series)

                elif isinstance(bt_data, pd.Panel):
                    if date not in bt_data.major_axis:
                        continue
                    df = bt_data.major_xs(date)
                    for sid, series in df.iterkv():
                        yield _build_event(date, sid, series)
            else:
                try:
                    snapshot = self.live.get_data(self.sids)
                except Exception as error:
                    raise LoadDataFailed(sids=self.sids, reason=error)
                for sid, series in snapshot.iterkv():
                    yield _build_event(date, sid, series)

    @property
    def instance_hash(self):
        return self.arg_string

    @property
    def raw_data(self):
        if not self._raw_data:
            self._raw_data = self.raw_data_gen()
        return self._raw_data
