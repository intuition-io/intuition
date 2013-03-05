import ipdb as pdb

import urllib2
import sys
import re
import os
import pytz

from pandas import Index, Series, DataFrame
from pandas.io.data import DataReader
import pandas as pd

import numpy as np

from xml.dom import minidom, Node
import json

from logbook import Logger

sys.path.append(os.environ['QTRADE'])
from neuronquant.data.QuantDB import yahooCode, Fields
from neuronquant.utils.dates import epochToDate
from neuronquant.utils.utils import reIndexDF


class Alias (object):
    #TODO: Uniform Quote dict structure to implement (and fill in different methods)
    #tmp
    SYMBOL = 't'
    MARKET = 'e'
    VALUE = 'l'
    DATE = 'lt'
    VARIATION = 'c'
    VAR_PER_CENT = 'cp'


#TODO 1. Every fetcher should take an index object, construct mostly with date_range
#TODO Use requests module to fetch remote data, cleaner http://docs.python-requests.org/en/latest/
class Fetcher(object):
    ''' Web access to data '''
    def __init__(self, timezone=pytz.utc, lvl='debug'):
        self.tz = timezone
        self.log = Logger(self.__class__.__name__)

    def getMinutelyQuotes(self, symbol, market, index):
        days = abs((index[index.shape[0] - 1] - index[0]).days)
        freq = int(index.freqstr[0])
        if index.freqstr[1] == 'S':
            freq += 1
        elif index.freqstr[1] == 'T':
            freq *= 61
        elif index.freqstr[1] == 'H':
            freq *= 3601
        else:
            self.log.error('** No suitable time frequency: {}'.format(index.freqstr))
            return None
        url = 'http://www.google.com/finance/getprices?q=%s&x=%s&p=%sd&i=%s' \
                % (symbol, market, str(days), str(freq + 1))
        self.log.info('On %d days with a precision of %d secs' % (days, freq))
        try:
            page = urllib2.urlopen(url)
        except urllib2.HTTPError:
            self.log.error('** Unable to fetch data for stock: %s'.format(symbol))
            return None
        except urllib2.URLError:
            self.log.error('** URL error for stock: %s'.format(symbol))
            return None
        feed = ''
        data = []
        while (re.search('^a', feed) is None):
            feed = page.readline()
        while (feed != ''):
            data.append(np.array(map(float, feed[:-1].replace('a', '').split(','))))
            feed = page.readline()
        dates, open, close, high, low, volume = zip(*data)
        adj_close = np.empty(len(close))
        adj_close.fill(np.NaN)
        data = {
                'open'      : open,
                'close'     : close,
                'high'      : high,
                'low'       : low,
                'volume'    : volume,
                'adj_close' : adj_close  # for compatibility with Fields.QUOTES
        }
        #NOTE use here index ?
        dates = Index(epochToDate(d) for d in dates)
        return DataFrame(data, index=dates.tz_localize(self.tz))

    def getHistoricalQuotes(self, symbol, index, market=None):
        assert (isinstance(index, pd.Index))
        source = 'yahoo'
        try:
            quotes = DataReader(symbol, source, index[0], index[-1])
        except:
            self.log.error('** Could not get {} quotes'.format(symbol))
            return pd.DataFrame()
        if index.freq != pd.datetools.BDay() or index.freq != pd.datetools.Day():
            #NOTE reIndexDF has a column arg but here not provided
            quotes = reIndexDF(quotes, delta=index.freq, reset_hour=False)
        if not quotes.index.tzinfo:
            quotes.index = quotes.index.tz_localize(self.tz)
        quotes.columns = Fields.QUOTES
        return quotes

    def get_stock_snapshot(self, symbols, markets, light=True):
        snapshot = {q: dict() for q in symbols}
        if light:
            data = self._lightSummary(symbols, markets)
        else:
            data = self._heavySummary(symbols)
        i = 0
        if not data:
            self.log.error('** No stock informations')
            return None
        for item in symbols:
            snapshot[item] = data[i]
            i += 1
        return snapshot

    def _lightSummary(self, symbols, markets):
        #TODO Finir de changer les index et comprendre tous les champs
        url = 'http://finance.google.com/finance/info?client=ig&q=%s:%s' \
                % (symbols[0], markets[0])
        for i in range(1, len(symbols)):
            url = url + ',%s:%s' % (symbols[i], markets[i])
        self.log.info('Retrieving light Snapshot from %s' % url)
        return json.loads(urllib2.urlopen(url).read()[3:], encoding='latin-1')

    def _heavySummary(self, symbols):
        url = 'http://www.google.com/ig/api?stock=' + symbols[0]
        for s in symbols[1:]:
            url = url + '&stock=' + s
        self.log.info('Retrieving heavy Snapshot from %s' % url)
        try:
            url_fd = urllib2.urlopen(url)
        except IOError:
            self.log.error('** Bad url: %s' % url)
            return None
        try:
            xml_doc = minidom.parse(url_fd)
            root_node = xml_doc.documentElement
        except:
            self.log.error('** Parsing xml google response')
            return None
        i = 0
        #snapshot = {q : dict() for q in symbols}
        snapshot = list()
        ticker_data = dict()
        for node in root_node.childNodes:
            if (node.nodeName != 'finance'):
                continue
            ticker_data.clear()
            for item_node in node.childNodes:
                if (item_node.nodeType != Node.ELEMENT_NODE):
                    continue
                ticker_data[item_node.nodeName] = item_node.getAttribute('data')
            i += 1
            snapshot.append(ticker_data)
        return snapshot

    #TODO: a separate class with functions per categories of data
    #NOTE: The YQL can fetch this data (http://www.yqlblog.net/blog/2009/06/02/getting-stock-information-with-%60yql%60-and-open-data-tables/)
    def getStockInfo(self, symbols, fields):
        for f in fields:
            #NOTE could just remove field and continue
            if f not in yahooCode:
                self.log.error('** Invalid stock information request.')
                return None
        #TODO: remove " from results
        #TODO A wrapper interface to have this document through ticker names
        #symbols, markets = self.db.getTickersCodes(index, quotes)
        fields.append('error')
        url = 'http://finance.yahoo.com/d/quotes.csv?s='
        url = url + '+'.join(symbols) + '&f='
        url += ''.join([yahooCode[item.lower()] for item in fields])
        data = urllib2.urlopen(url)
        df = dict()
        for item in symbols:
            #FIXME: ask size return different length arrays !
            df[item] = Series(data.readline().strip().strip('"').split(','), index=fields)
        return DataFrame(df)
