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


import time
import datetime as dt
import pytz
import calendar
from dateutil.parser import parse

import pandas as pd
from pandas.core.datetools import BMonthEnd

#import babel.numbers
#import decimal


#TODO Handle in-day dates, with hours and minutes
def normalize_date_format(date):
    '''
    Dates can be defined in many ways, but zipline use
    aware datetime objects only. Plus, the software work
    with utc timezone so we convert it.
    __________________________________________________
    Parameters
        date: str
            String date, see dateutils module for precisions
    __________________________________________________
    Return
        datetime.datetime utc tz aware object
    '''
    assert isinstance(date, str) or isinstance(date, unicode)
    local_tz = pytz.timezone(_detect_timezone())
    local_dt = local_tz.localize(parse(date), is_dst=None)
    return local_dt.astimezone(pytz.utc)

    #locale_date = parse(date)
    #if locale_date.tzinfo is None:
        #locale_date = locale_date.replace(
            #tzinfo=pytz.timezone(_detect_timezone()))
    ##FIXME astimezone() retieve 8 minutes from Paris timezone Oo 20 from
    ##      Amsterdam WTF
    #return locale_date.astimezone(pytz.utc)


def _detect_timezone():
    '''
    Experimental and temporary (since there is a world module)
    get timezone as set by the system
    '''
    import locale
    locale_code = locale.getdefaultlocale()[0]
    #return str(pytz.country_timezones[locale_code[:2]][0])
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


def UTCdateToEpoch(utc_date):
    return calendar.timegm(utc_date.timetuple())


def dateToEpoch(local_date):
    return time.mktime(local_date.timetuple())


def epochToDate(epoch, tz=pytz.utc):
    tm = time.gmtime(epoch)
    return(dt.datetime(tm.tm_year, tm.tm_mon, tm.tm_mday,
           tm.tm_hour, tm.tm_min, tm.tm_sec, 0, tz))


def dateFormat(epoch):
    ''' Convert seconds of epoch time to date POSIXct format %Y-%M-%D %H:%m '''
    return time.strftime("%Y-%m-%d %H:%M", time.localtime(epoch))


def toMonthly(frame, how):
    #TODO: generic function ?
    offset = BMonthEnd()
    return frame.groupby(offset.rollforward).aggregate(how)


def getOffset(values):
    #Inspect pandas to figure out a much better method
    ''' Transform delta, Serie, Dataframe and dates into Offset '''
    assert (len(values) > 0)
    if isinstance(values, dt.timedelta):
        delta = values
    elif isinstance(values, pd.DataFrame) or isinstance(values, pd.Series):
        delta = values.index[1] - values.index[0]
    elif isinstance(values[0], dt.datetime):
        assert (len(values) > 1)
        delta = values[1] - values[0]
    else:
        raise ValueError()
    assert(delta.days != 0 or delta.seconds != 0)
    rest = delta.days % 30
    if delta.seconds > 0 and delta.days == 0:
        offset = pd.datetools.Minute(delta.seconds * 60)
    elif delta.days < 5:
        offset = pd.datetools.BDay(delta.days)
    elif rest < 5 or rest > 25:
        offset = pd.datetools.BMonthEnd(int(round(float(delta.days) / 30.0)))
    else:
        offset = pd.datetools.BDay(delta.days)
    #NOTE useful ?
    #return pd.DateOffset(days=delta.days, minutes=delta.seconds*60)
    return offset


def dateToIndex(dates, tz=pytz.utc):
    assert (len(dates) > 1)
    assert (isinstance(dates[0], dt.datetime))
    index = pd.date_range(dates[0], dates[-1], freq=getOffset(dates))
    if not dates[0].tzinfo:
        return index.tz_localize(tz)
    return index
