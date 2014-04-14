# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Intuition misc utilities
  ------------------------

  :copyright (c) 2014 Xavier Bruhiere
  :license: Apache 2.0, see LICENSE for more details.
'''


import time
import datetime as dt
import pytz
import pandas as pd
import dna.utils
from dna.time_utils import normalize_date_format


def is_live(current_date):
    ''' True if the given date is in the (utc) future '''
    return (current_date > pd.datetime.now(pytz.utc))


def next_tick(date, interval=15):
    '''
    Only return when we reach given datetime
    '''
    # Intuition works with utc dates, conversion are made for I/O
    now = dt.datetime.now(pytz.utc)
    live = False
    # Sleep until we reach the given date
    while now < date:
        time.sleep(interval)
        # Update current time
        now = dt.datetime.now(pytz.utc)
        # Since we're here, we waited a future date, so this is live trading
        live = True
    return live


def intuition_module(location):
    ''' Build the module path and import it '''
    path = location.split('.')
    # Get the last field, i.e. the object name in the file
    obj = path.pop(-1)
    return dna.utils.dynamic_import('.'.join(path), obj)


# NOTE Without the freq param, their might be some smart refactor to do here
def build_trading_timeline(start, end):
    ''' Build the daily-based index we will trade on '''
    EMPTY_DATES = pd.date_range('2000/01/01', periods=0, tz=pytz.utc)
    now = dt.datetime.now(tz=pytz.utc)

    if not start:
        if not end:
            # Live trading until the end of the day
            bt_dates = EMPTY_DATES
            live_dates = pd.date_range(
                start=now,
                end=normalize_date_format('23h59'))
        else:
            end = normalize_date_format(end)
            if end < now:
                # Backtesting since a year before end
                bt_dates = pd.date_range(
                    start=end - 360 * pd.datetools.day,
                    end=end)
                live_dates = EMPTY_DATES
            elif end > now:
                # Live trading from now to end
                bt_dates = EMPTY_DATES
                live_dates = pd.date_range(start=now, end=end)
    else:
        start = normalize_date_format(start)
        if start < now:
            if not end:
                # Backtest for a year or until now
                end = start + 360 * pd.datetools.day
                if end > now:
                    end = now - pd.datetools.day
                live_dates = EMPTY_DATES
                bt_dates = pd.date_range(
                    start=start, end=end)
            else:
                end = normalize_date_format(end)
                if end < now:
                    # Nothing to do, backtest from start to end
                    live_dates = EMPTY_DATES
                    bt_dates = pd.date_range(start=start, end=end)
                elif end > now:
                    # Hybrid timeline, backtest from start to end, live
                    # trade from now to end
                    bt_dates = pd.date_range(
                        start=start, end=now - pd.datetools.day)

                    live_dates = pd.date_range(start=now, end=end)
        elif start > now:
            if not end:
                # Live trading from start to the end of the day
                bt_dates = EMPTY_DATES
                live_dates = pd.date_range(
                    start=start,
                    end=normalize_date_format('23h59'))
            else:
                # Live trading from start to end
                end = normalize_date_format(end)
                bt_dates = EMPTY_DATES
                live_dates = pd.date_range(start=start, end=end)

    return bt_dates + live_dates
