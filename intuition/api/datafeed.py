# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Intuition Data source api
  -------------------------

  Data generator motherboard for Intuition. It uses backtest and live data
  sources to build the datafeed of the algorithm.

  :copyright (c) 2014 Xavier Bruhiere
  :license: Apache 2.0, see LICENSE for more details.
'''

import pandas as pd
import dna.logging
from zipline.sources.data_source import DataSource
from zipline.gens.utils import hash_args
import intuition.utils as utils
import intuition.data.universe as universe
from intuition.errors import LoadDataFailed, InvalidDatafeed


def _build_safe_event(event, date, sid):
    event.update({
        'dt': date,
        'sid': sid,
        'volume': event.get('volume', 1000)
    })
    return event


class HybridDataFactory(DataSource):
    '''
    Surcharge of zipline.DataSource, switching automatically between live
    stream and backtest sources
    '''
    _is_live = False

    def __init__(self, index, market, frequency):
        self.backtest = None
        self.live = None

        # TODO Use alternatives to `index` and `market` objects
        self.log = dna.logging.logger(__name__)
        self.frequency = frequency

        self.index = index
        self.start = self.index[0]
        self.end = self.index[-1]
        self.sids = market.sids
        self.market_open = market.open
        self.market_close = market.close
        self.market_timezone = market.timezone

        # Hash_value for downstream sorting.
        self.arg_string = hash_args({'index': index, 'market': market})
        self._raw_data = None

    def check_sources(self):
        # TODO Fails if the class has no get_data method
        if not self.backtest and not self.live:
            raise InvalidDatafeed(
                reason='provide at least a backtest or a live data module'
            )

        if not self.backtest and not utils.is_live(self.start):
            raise InvalidDatafeed(
                reason='no backtest data source provided for past dates')

        if not self.live and utils.is_live(self.end):
            raise InvalidDatafeed(
                reason='no live data source provided for futur dates'
            )

    # NOTE We overwrite source but it should be possible to append them
    # TODO Validate here data source
    # TODO Validate we have at least a backtest or live source
    def add_source(self, mode, path, **kwargs):
        source_module = utils.intuition_module(path)
        if mode == 'live':
            self.live = source_module(self.sids, kwargs)
        elif mode == 'backtest':
            self.backtest = source_module(self.sids, kwargs)
        else:
            raise ValueError('Invalid source mode: {}'.format(mode))

    @property
    def mapping(self):
        if self._is_live:
            return self.live.mapping
        else:
            return self.backtest.mapping

    def _get_backtest_data(self):
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
        return bt_data

    def _agnostic_get_data_at(self, date, data):
        dated_data = pd.DataFrame()
        n_axes = len(data.axes)

        if self._is_live:
            try:
                dated_data = self.live.get_data(self.sids)
            except Exception as error:
                raise LoadDataFailed(sids=self.sids, reason=error)

            if isinstance(dated_data, pd.Series):
                dated_data = pd.DataFrame(
                    {sid: {'price': price}
                     for sid, price in dated_data.iterkv()})

        else:
            midnight_date = pd.datetools.normalize_date(date)
            if n_axes == 2:
                if midnight_date in data.index:
                    dated_data = pd.DataFrame(
                        {sid: {'price': price}
                         for sid, price in data.ix[midnight_date].iterkv()})

            elif n_axes == 3:
                if midnight_date in data.major_axis:
                    dated_data = data.major_xs(midnight_date)

            else:
                raise TypeError('only dataframe and panel are supported')
        return dated_data

    def raw_data_gen(self):
        bt_data = self._get_backtest_data()

        for date in self.index:
            backtest_is_done = False
            open_hour = date.replace(hour=self.market_open.hour,
                                     minute=self.market_open.minute)
            close_hour = date.replace(hour=self.market_close.hour,
                                      minute=self.market_close.minute)

            tick_ = universe.Tick(
                start=open_hour, end=close_hour, tz=self.market_timezone
            )
            tick_.parse(self.frequency)

            # Trade until the end of the trading day
            for date in tick_.tack:
                # Set to opening of the market
                self.log.debug('--> next tick {}'.format(date))
                # NOTE Make _is_live a property ?
                self._is_live = utils.next_tick(date)

                data = self._agnostic_get_data_at(date, bt_data)
                if not data.empty:
                    for sid, series in data.iterkv():
                        if backtest_is_done and not self._is_live:
                            # TODO Use previous and next data to extrapolate
                            # random values
                            self.log.debug('extrapoling intraday data')

                        yield _build_safe_event(series.to_dict(), date, sid)
                    backtest_is_done = True

    @property
    def instance_hash(self):
        return self.arg_string

    @property
    def raw_data(self):
        if not self._raw_data:
            self._raw_data = self.raw_data_gen()
        return self._raw_data
