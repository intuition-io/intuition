import locale
import datetime
import pytz

#import babel.numbers
#import decimal
from pycurrency import converter
import ccy

from decorators import *

#TODO: A class for common methods and a currency object ?
#TODO: inheritant from ccy.currency ?
#NOTE: a simple convert function is available
class Currency(object):
    def __init__(self, country_code='fr', cross='usd', conv=None):
        self.cross = cross
        self.ccy_code = ccy.countryccy(country_code)
        self.money = ccy.currency(self.ccy_code)
        self.engine = converter.Converter(1, self.money.code, cross)
        if conv == None:
            locale.setlocale(locale.LC_ALL, '')
            conv = locale.localeconv()
        self.conv = conv
        self.symbol = locale.nl_langinfo(locale.CRNCYSTR)[1:]

    def getInfos(self):
        self.money.printinfo()

    def getRateExchange(self, from_ccy='default', to_ccy='usd'):
        return self.convert(1, from_ccy, to_ccy)

    @limitPerf(0.001)
    def convert(self, amount = 1, from_ccy='default', to_ccy='usd'):
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
        days_sym = [locale.DAY_1, locale.DAY_2, locale.DAY_3, locale.DAY_4, locale.DAY_5, locale.DAY_6, locale.DAY_7]
        months_sym = [locale.DAY_1, locale.DAY_2, locale.DAY_3, locale.DAY_4, locale.DAY_5, locale.DAY_6, \
        locale.DAY_7, locale.MON_8, locale.MON_9, locale.MON_10, locale.MON_11, locale.MON_12]
        self.days = [locale.nl_langinfo(d) for d in days_sym]
        self.months = [locale.nl_langinfo(d) for d in months_sym]
        if conv == None:
            locale.setlocale(locale.LC_ALL, '')
        self.date_fmt = locale.nl_langinfo(locale.D_FMT) + ' %Z%z'
        self.hour_fmt = locale.nl_langinfo(locale.T_FMT) + ' %Z%z'
        self.datetime_fmt = locale.nl_langinfo(locale.D_T_FMT) + ' %Z%z'
        
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
        return datetime.datetime(year, month, day, hour, min, sec, tzinfo=pytz.timezone(tz)).strftime(self.datetime_fmt)

    def jetlagConvert(self, date, code):
        #TODO: ask for country code and convert to tz ?
        dt = self.tz.localize(date)
        tz = pytz.timezone(pytz.country_timezones[code][0])
        return dt.astimezone(tz).strftime(self.datetime_fmt)

    def actualize(self, tz):
        #TODO: change formats here after setTimezone()
        return 'not implemented'

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
        if code == None:
            return self.currency
        else:
            return Currency(code)

    def getTimezone(self, code=None):
        if code == None:
            return self.jetLag
        else:
            return TimeZone(code)
