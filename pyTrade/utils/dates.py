import ipdb as pdb

import time
import datetime as dt
import pytz
import calendar

import pandas as pd
from pandas import DataFrame
from pandas.core.datetools import BMonthEnd

#import babel.numbers
#import decimal


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


def dateToIndex(dates, tz=pytz.tz):
    assert (len(dates) > 1)
    assert (isinstance(dates[0], dt.datetime))
    index = pd.date_range(dates[0], dates[-1], freq=getOffset(dates))
    if not dates[0].tzinfo:
        return index.tz_localize(tz)
    return index
