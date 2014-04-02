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
import dateutil.parser
import pandas as pd
import dna.utils


def is_live(current_date):
    return (current_date > pd.datetime.now(pytz.utc))


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

    #assert isinstance(date, str) or isinstance(date, unicode)
    if isinstance(date, str) or isinstance(date, unicode):
        date = dateutil.parser.parse(date)
    assert isinstance(date, dt.datetime)
    local_tz = pytz.timezone(_detect_timezone())
    local_dt = local_tz.localize(date, is_dst=None)
    #local_dt = local_tz.localize(parse(date), is_dst=None)
    return local_dt.astimezone(pytz.utc)


def _detect_timezone():
    '''
    Experimental and temporary (since there is a world module)
    get timezone as set by the system
    '''
    default_timezone = 'America/New_York'
    locale_code = locale.getdefaultlocale()
    return default_timezone if not locale_code else \
        str(pytz.country_timezones[locale_code[0][-2:]][0])


def build_date_index(start='', end='', freq='D'):
    #import ipdb; ipdb.set_trace()
    #TODO Only 'D' for backtest and '1min' for live are supported
    now = dt.datetime.now(tz=pytz.utc)
    if not start:
        if not end:
            # Live trading until the end of the day
            start = now
            end = now.replace(hour=23, minute=00, second=0)
            freq = '1min'
        else:
            if end > now:
                # Live trading from now to end
                start = now
                freq = '1min'
            else:
                # Backtest for a year
                start = end - 360 * pd.datetools.day
    else:
        # Only backtests support start information
        if not end:
            # Backtest for a year or until now
            end = start + 360 * pd.datetools.day
            if end > now:
                end = now
        else:
            assert start < end
    return pd.date_range(start, end, freq=freq)


def UTC_date_to_epoch(utc_date):
    return calendar.timegm(utc_date.timetuple())


def epoch_to_date(epoch, tz=pytz.utc):
    tm = time.gmtime(epoch)
    return(dt.datetime(tm.tm_year, tm.tm_mon, tm.tm_mday,
           tm.tm_hour, tm.tm_min, tm.tm_sec, 0, tz))


def next_tick(date, interval=15):
    '''
    Only return when we reach given datetime
    '''
    # Intuition works with utc dates, conversion are made for I/O
    now = dt.datetime.now(pytz.utc)
    live = False
    while now < date:
        time.sleep(interval)
        now = dt.datetime.now(pytz.utc)
        live = True
    return live


def intuition_module(location):
    ''' Build the module path and import it '''
    path = location.split('.')
    obj = path.pop(-1)
    return dna.utils.dynamic_import('.'.join(path), obj)


def truncate(float_value, n=2):
    if isinstance(float_value, float):
        float_value = float('%.*f' % (n, float_value))
    return float_value
