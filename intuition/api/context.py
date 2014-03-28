# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Intuition Context api
  ---------------------

  Context factory api.

  :copyright (c) 2014 Xavier Bruhiere
  :license: Apache 2.0, see LICENSE for more details.
'''


import abc
import pytz
import datetime as dt
import pandas as pd
import dna.logging
import intuition.utils

EMPTY_DATES = pd.date_range('2000/01/01', periods=0, tz=pytz.utc)


def parse_storage(storage):
    tmp_uri = storage.split('?')
    path = tmp_uri[0].split('/')[1:]
    uri = tmp_uri[0].split('/')[0]

    params = {}
    if len(tmp_uri) > 1:
        tmp_params = tmp_uri[1].split('&')
        for item in tmp_params:
            k, v = item.split('=')
            params[k] = v

    return {
        'uri': uri,
        'path': path,
        'param': params
    }


class ContextFactory():
    '''
    Contexts loader gives to intuition everything it needs to know about user
    configuration. It also provides some methods to make the setup process
    easier (like the interpreting the shortcut 'nasdaq,6' into 6 random symbols
    from nasdaq exchange).
    '''

    __metaclass__ = abc.ABCMeta

    def __init__(self, storage):
      # TODO Check storage syntax
        self.log = dna.logging.logger(__name__)
        self.initialize(parse_storage(storage))

    def initialize(self, storage):
        ''' Users should overwrite this method '''
        pass

    @abc.abstractmethod
    def load(self, uri, path, params):
        ''' Users should overwrite this method '''
        pass

    def _normalize_context(self, context):
        if 'start' in context:
            if isinstance(context['start'], dt.date):
                context['start'] = dt.date.strftime(
                    context['start'], format='%Y-%m-%d')
        if 'end' in context:
            if isinstance(context['end'], dt.date):
                context['end'] = dt.date.strftime(
                    context['end'], format='%Y-%m-%d')
        context['frequency'] = context.get('frequency', 'D')

        # TODO Check if 'frequency' available
        trading_dates = self._build_trading_timeline(
            context.pop('start', None), context.pop('end', None),
            context['frequency'])

        context['index'] = trading_dates
        context['live'] = (dt.datetime.now(tz=pytz.utc) < trading_dates[-1])

    # TODO Frequency for live trading (and backtesting ?)
    def _build_trading_timeline(self, start, end, freq):
        now = dt.datetime.now(tz=pytz.utc)

        if not start:
            if not end:
                # Live trading until the end of the day
                bt_dates = EMPTY_DATES
                live_dates = intuition.utils.build_date_index(
                    start=now,
                    end=intuition.utils.normalize_date_format('23h'),
                    freq=freq)
            else:
                end = intuition.utils.normalize_date_format(end)
                if end < now:
                    # Backtesting since a year before end
                    bt_dates = intuition.utils.build_date_index(
                        start=end - 360 * pd.datetools.day,
                        end=end)
                    live_dates = EMPTY_DATES
                elif end > now:
                    # Live trading from now to end
                    bt_dates = EMPTY_DATES
                    live_dates = intuition.utils.build_date_index(
                        start=now, end=end, freq=freq)
        else:
            start = intuition.utils.normalize_date_format(start)
            if start < now:
                if not end:
                    # Backtest for a year or until now
                    end = start + 360 * pd.datetools.day
                    if end > now:
                        end = now - pd.datetools.day
                    live_dates = EMPTY_DATES
                    bt_dates = intuition.utils.build_date_index(
                        start=start, end=end)
                else:
                    end = intuition.utils.normalize_date_format(end)
                    if end < now:
                        # Nothing to do, backtest from start to end
                        live_dates = EMPTY_DATES
                        bt_dates = intuition.utils.build_date_index(
                            start=start,
                            end=end)
                    elif end > now:
                        # Hybrid timeline, backtest from start to end, live
                        # trade from now to end
                        bt_dates = intuition.utils.build_date_index(
                            start=start, end=now-pd.datetools.day)

                        live_dates = intuition.utils.build_date_index(
                            start=now, end=end, freq=freq)
            elif start > now:
                if not end:
                    # Live trading from start to the end of the day
                    bt_dates = EMPTY_DATES
                    live_dates = intuition.utils.build_date_index(
                        start=start,
                        end=intuition.utils.normalize_date_format('23h'),
                        freq=freq)
                else:
                    # Live trading from start to end
                    end = intuition.utils.normalize_date_format(end)
                    bt_dates = EMPTY_DATES
                    live_dates = intuition.utils.build_date_index(
                        start=start,
                        end=end, freq=freq)

        return bt_dates + live_dates

    def _normalize_strategy(self, strategy):
        ''' some contexts only retrieves strings, giving back right type '''
        for k, v in strategy.iteritems():
            if v == 'true':
                strategy[k] = True
            elif v == 'false' or v is None:
                strategy[k] = False
            else:
                try:
                    strategy[k] = float(v)
                except ValueError:
                    pass

    def build(self):
        context = self.load()

        algorithm = context.pop('algorithm', {})
        manager = context.pop('manager', {})
        data = context.pop('data', {})

        if context:
            self._normalize_context(context)
        if algorithm:
            self._normalize_strategy(algorithm)
        if manager:
            self._normalize_strategy(manager)

        strategy = {
            'algorithm': algorithm,
            'manager': manager,
            'data': data
        }

        return context, strategy
