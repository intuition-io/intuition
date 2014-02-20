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
import calendar
import locale
from dateutil.parser import parse
import pandas as pd


def is_live(last_trade):
    return (last_trade > pd.datetime.now(pytz.utc))


#TODO Handle in-day dates, with hours and minutes
def normalize_date_format(date):
    '''
    Dates can be defined in many ways, but zipline use
    aware datetime objects only. Plus, the software work
    with utc timezone so we convert it.
    '''
    if isinstance(date, int):
        # This is probably epoch time
        date = time.strftime('%Y-%m-%d %H:%M:%S',
                             time.localtime(date))

    assert isinstance(date, str) or isinstance(date, unicode)
    local_tz = pytz.timezone(_detect_timezone())
    local_dt = local_tz.localize(parse(date), is_dst=None)
    return local_dt.astimezone(pytz.utc)


def _detect_timezone():
    '''
    Experimental and temporary (since there is a world module)
    get timezone as set by the system
    '''
    locale_code = locale.getdefaultlocale()[0]
    return str(pytz.country_timezones[locale_code[-2:]][0])


def build_date_index(start='', end='', freq='D'):
    #TODO Only 'D' for backtest and '1min' for live are supported
    now = dt.datetime.now(tz=pytz.utc)
    if not start:
        if not end:
            # Live trading until the end of the day
            start = now
            end = now.replace(hour=23, minute=59, second=0)
            freq = '1min'
        else:
            end = normalize_date_format(end)
            if end > now:
                # Live trading from now to end
                start = now
                freq = '1min'
            else:
                # Backtest for a year
                start = end - 360 * pd.datetools.day
    else:
        # Only backtests support start information
        start = normalize_date_format(start)
        if not end:
            # Backtest for a year or until now
            end = start + 360 * pd.datetools.day
            if end > now:
                end = now
        else:
            end = normalize_date_format(end)
            assert start < end
    return pd.date_range(start, end, freq=freq)


def UTC_date_to_epoch(utc_date):
    return calendar.timegm(utc_date.timetuple())


def epoch_to_date(epoch, tz=pytz.utc):
    tm = time.gmtime(epoch)
    return(dt.datetime(tm.tm_year, tm.tm_mon, tm.tm_mday,
           tm.tm_hour, tm.tm_min, tm.tm_sec, 0, tz))
