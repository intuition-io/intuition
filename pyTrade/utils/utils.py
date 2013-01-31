import ipdb as pdb

import locale
import time
import datetime as dt
import pytz
import calendar

import pandas as pd
from pandas import DataFrame
from pandas.core.datetools import BMonthEnd
import numpy as np

#import babel.numbers
#import decimal
from pycurrency import converter
import ccy

from decorators import *

'''___________________________________________________________________________________    Logging    ________'''
# Distributed logging with zeroMQ
import os
from logbook import Logger
from logbook import NestedSetup, FileHandler, Processor, StderrHandler


def inject_information(record):
    record.extra['ip'] = '127.0.0.1'

# a nested handler setup can be used to configure more complex setups
setup = NestedSetup([
    StderrHandler(format_string=u'[{record.time:%Y-%m-%d %H:%M}]{record.channel} - {record.level_name}: {record.message} \t({record.extra[ip]})'),
    # then write messages that are at least warnings to to a logfile
    FileHandler(os.environ['QTRADE_LOG'], level='WARNING'),
    Processor(inject_information)
])
log = Logger('Trade Labo')
'''__________________________________________________________________________________________________________'''

class Currency(object):
    #TODO: A class for common methods and a currency object ?
    #TODO: inheritant from ccy.currency ?
    #NOTE: a simple convert function is available
    def __init__(self, country_code='fr', cross='usd', conv=None):
        self.cross = cross
        self.ccy_code = ccy.countryccy(country_code)
        self.money = ccy.currency(self.ccy_code)
        self.engine = converter.Converter(1, self.money.code, cross)
        if conv is None:
            locale.setlocale(locale.LC_ALL, '')
            conv = locale.localeconv()
        self.conv = conv
        self.symbol = locale.nl_langinfo(locale.CRNCYSTR)[1:]

    def getInfos(self):
        self.money.printinfo()

    def getRateExchange(self, from_ccy='default', to_ccy='usd'):
        return self.convert(1, from_ccy, to_ccy)

    @limitPerf(0.001)
    def convert(self, amount=1, from_ccy='default', to_ccy='usd'):
        if from_ccy == 'default':
            self.engine.from_cur = self.ccy_code
            self.engine.to_cur = self.cross
        else:
            self.engine.from_cur = from_ccy
            self.engine.to_cur = to_ccy
        self.engine.amount = amount
        self.engine.update()
        return self.engine.result()[0]

    def getCurrency(self):
        return self.engine.query['from']

    def CcyFormat(self, value):
        #return babel.numbers.format_currency(decimal.Decimal(str(value)), self.money.code)
        #return locale.format_string('%s%.*f', (conv['currency_symbol'], conv['frac_digits'], value), grouping=True)
        return locale.currency(value, self.conv, grouping=True)


class TimeZone(object):
    def __init__(self, code='fr', conv=None):
        self.tz = pytz.timezone(pytz.country_timezones[code][0])
        days_sym = [locale.DAY_1, locale.DAY_2, locale.DAY_3, locale.DAY_4,
                    locale.DAY_5, locale.DAY_6, locale.DAY_7]
        months_sym = [locale.DAY_1, locale.DAY_2, locale.DAY_3, locale.DAY_4,
                      locale.DAY_5, locale.DAY_6, locale.DAY_7, locale.MON_8,
                      locale.MON_9, locale.MON_10, locale.MON_11, locale.MON_12]
        self.days = [locale.nl_langinfo(d) for d in days_sym]
        self.months = [locale.nl_langinfo(d) for d in months_sym]
        if conv is None:
            locale.setlocale(locale.LC_ALL, '')
        self.date_fmt = locale.nl_langinfo(locale.D_FMT) + ' %Z%z'
        self.hour_fmt = locale.nl_langinfo(locale.T_FMT) + ' %Z%z'

    def setTimezone(self, tz):
        self.tz = pytz.timezone(tz)
        self.actualize(tz)

    def getLocaleDate(self, dt):
        #return time.strftime(self.date_fmt, t)
        return self.tz.localize(dt).strftime(self.date_fmt)

    def getLocaleTime(self, dt):
        return self.tz.localize(dt).strftime(self.hour_fmt)

    def getLocaleDateTime(self, dt):
        return self.tz.localize(dt).strftime(self.datetime_fmt)

    def jetlagConvert2(self, tz, year, month, day, hour=0, min=0, sec=0):
        return dt.datetime(year, month, day, hour, min, sec,
                           tzinfo=pytz.timezone(tz)).strftime(self.datetime_fmt)

    def jetlagConvert(self, date, code):
        #TODO: ask for country code and convert to tz ?
        dt = self.tz.localize(date)
        tz = pytz.timezone(pytz.country_timezones[code][0])
        return dt.astimezone(tz).strftime(self.datetime_fmt)

    def actualize(self, tz):
        #TODO: change formats here after setTimezone()
        return 'not implemented'


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


def BIndexGenerator(start, end, delta=pd.datetools.bday, market=''):
    '''
    @summary generate a business index, avoiding closed market days and hours
    @param start, end, delta: dates informations
    @param market: the concerned market, t guess hours
    @return: a formatted pandas index
    '''
    if delta >= pd.datetools.BDay():
        start += dt.timedelta(hours=23 - start.hour)
    #Business date_range doesn't seem to work
    bdays = pd.date_range(start, end, freq=delta)
    # TODO: Substracting special days like christmas
    if bdays.freq > pd.datetools.Day():
        selector = ((dates.hour > 8) & (dates.hour < 17)) | \
                   ((dates.hour > 16) & (dates.hour < 18) &
                   (dates.minute < 31))
        #return bdays[Markets('euronext').schedule()['selector']]
        return bdays[selector]
    return bdays


def reIndexDF(df, **kwargs):
    '''
    @summary take a pandas dataframe and reformat
    it according to delta, start and end,
    contrained by closed market days and hours
    '''
    how = kwargs.get('how', np.mean)
    start = kwargs.get('start', df.index[0])
    end = kwargs.get('end', df.index[-1])
    delta_tmp = kwargs.get('delta', df.index[1] - df.index[0])
    market = kwargs.get('market', 'euronext')
    columns = kwargs.get('columns', None)
    if df.index.tzinfo:
        tz = df.index.tzinfo
    else:
        tz = pytz.utc
    assert (not df.empty)
    assert (isinstance(start, dt.datetime) and isinstance(end, dt.datetime))
    assert (isinstance(market, str))
    assert (isinstance(columns, list) or not columns)
    if delta_tmp is None:
        delta_tmp = df.index[1] - df.index[0]
    if isinstance(delta_tmp, dt.timedelta):
        #TODO more offset std or a new way to do it
        if abs(delta_tmp.days - 30) < 5:
            delta = BMonthEnd()
        else:
            delta = pd.DateOffset(days=delta_tmp.days,
                                  minutes=delta_tmp.seconds * 60)
    elif isinstance(delta_tmp, pd.datetools.DateOffset):
        delta = delta_tmp
    else:
        raise ValueError()
    print('[DEBUG] reIndexDF : re-indexing to -> Start: {}, end: {}, delta: {}'
          .format(start, end, delta))
    #if columns:
        #return df.reindex(index = BIndexGenerator(start, end, delta, market), columns=columns).dropna(axis=0)
    #return df.reindex(index=BIndexGenerator(start, end, delta, market))
    if columns:
        df = DataFrame(df.groupby(delta.rollforward).aggregate(how),
                       columns=columns)
    else:
        #FIXME When delta almost the same, error, regular error
        if kwargs.get('reset_hour', False):
            rst_idx = pd.date_range(df.index[0] - pd.datetools.relativedelta(hours=df.index[0].hour),
                df.index[-1] - pd.datetools.relativedelta(hours=df.index[0].hour), freq=delta_tmp)
            df = pd.DataFrame(df, index=rst_idx)
        elif delta.freqstr[-1] == 'M' and abs((df.index[1] - df.index[0]).days - 30) < 5:
            pass
        else:
            df = df.groupby(delta.rollforward).aggregate(how)
    #return df.truncate(before=(start-delta), after=end)
    df = df[(start - delta):end]
    if not df.index.tzinfo:
        df.index = df.index.tz_localize(tz)
    return df


class Markets:
    def __init__(self, market):
        self.selector = None
        self.market = market

    def schedule(self):
        #TODO: getting this values from database
        if self.market == 'euronext':
            selector = ((dates.hour > 8) & (dates.hour < 17)) | \
                       ((dates.hour > 16) & (dates.hour < 18) &
                        (dates.minute < 31))
            open = dt.time(9, 0, 0, 0)
            close = dt.time(17, 30, 0, 0)
        return {'open': open, 'close': close, 'simple fixing': '',
                'double fixing': '', 'selector': selector}


class International(object):
    #TODO: Handle the definition of an other localisation
    #TODO: Gessing the timezone ?
    #TODO: Use a namedtuple derived class ?
    def __init__(self, country_code=None):
        if country_code:
            self.country_code = country_code
            self.tz = pytz.country_timezones[country_code][0]
            self.country = pytz.country_names[country_code]
            #self.country = ccy.country(country_code)
            #TODO: self.lang not define
        else:
            self.lang, self.encoding = locale.getdefaultlocale()
            self.country_code = self.lang.split('_')[1]
        #TODO: specific localisation to handle
        locale.setlocale(locale.LC_ALL, '')
        conv = locale.localeconv()
        self.currency = Currency(self.country_code, 'USD', conv)
        self.jetLag = TimeZone(self.country_code, conv)

    def getCurrency(self, code=None):
        if code is None:
            return self.currency
        else:
            return Currency(code)

    def getTimezone(self, code=None):
        if code is None:
            return self.jetLag
        else:
            return TimeZone(code)
