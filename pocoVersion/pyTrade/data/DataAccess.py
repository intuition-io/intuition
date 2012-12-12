#!/usr/bin/python
# -*- coding: utf8 -*-

import urllib2
import sys, re, time
import datetime as dt

from pandas import Index, DataFrame, Panel
from pandas.core.datetools import BMonthEnd
from pandas import ols

import numpy as np
import matplotlib.finance as fin

from xml.dom import minidom, Node
from lxml import etree

import json

#TODO: use here env variable ?
sys.path.append('..')
from Utilities import LogSubSystem
from QantBase import QantBase

#TODO: Uniform Quote dict structure to implement (and fill in different methods)
#TODO: Implement yahoo framework: http://www.goldb.org/ystockquote.html
#TODO: Implement google, or other, currency conversion
#TODO: Historical data not available on french market ?? (cf archos)

#TODO A dedicated module or file storing theses functions (see QSTK)
def epochToDate(epoch):
    tm = time.gmtime(epoch)
    return(dt.datetime(tm.tm_year, tm.tm_mon, tm.tm_mday, tm.tm_hour, tm.tm_min))

def dateFormat(epoch):
    ''' Convert seconds of epoch time to date POSIXct format %Y-%M-%D %H:%m '''
    return time.strftime("%Y-%m-%d %H:%M", time.localtime(epoch))

class Alias (object):
    SYMBOL = 't'
    MARKET = 'e'
    VALUE = 'l'
    DATE = 'lt'
    VARIATION = 'c'
    VAR_PER_CENT = 'cp'


class DataAccess(object):
    ''' Quote object - fill everything related:
            name, code, current value, bought value,
            market, actions owned,
            and date, open, close, volume, of asked period'''
    # Handling different sources like in QSTK ?
    def __init__(self, db_location=None, logger=None):
        # Logger initialisation
        if logger == None:
          self._logger = LogSubSystem('QuoteDL', "debug").getLog()
        else:
          self._logger = logger
        #TODO: Trouver ici la database, boulot du prochain module
        if db_location != None:
            self._db = QantBase(db_location)
            self._logger.info('Database location provided, Connected to %s' % db_location)

    def getQuotes(self, quotes, fields, index=None, *args, **kwarg):
        ''' 
        @summary: retrieve google finance data asked while initializing
        and store it: Date, open, low, high, close, volume 
        @param quotes: list of quotes to fill
        @param fields: list of fields to store per quotes
        @param index: pandas.Index object, used for dataframes
        @param args: unuse
        @param kwargs.start: date or datetime of the first values
               kwargs.end: date or datetime of the last value
               kwargs.elapse: datetime.timedelta object, period of time to fill
        @return a panel/dataframe/timeserie like closeAt9 = data['google'][['close']][date]
        '''
        df = dict()
        #TODO: multithread !
        for q in quotes:
            self._logger.info('Processing %s stock' % q)
            # Compute start, end, elapse, whatever the parameters
            res = self._db.getData('stocks', {'ticker': q}, ("symbol","market"))
            symbol = 'GOOG'
            market = 'NASDAQ'
            if index != None:
                kwarg['start'] = index[0]
                kwarg['end'] = index[len(index)-1]
                kwarg['elapse'] = index[1] - index[0]  #timedelta object ?
            else:
                if 'end' not in kwarg:
                    kwarg['end'] = dt.datetime.now()
                if 'start' in kwarg:
                    if 'elapse' not in kwarg:
                        kwarg['elapse'] = self._guessResolution(kwarg['start'], kwarg['end'])
                elif 'start' not in kwarg:
                    if 'elapse' in kwarg:
                        kwarg['start'] = kwarg['end'] - kwarg['elapse']
                    else:
                        self._logger.error('** Neither start, end and elapse parameters provided')
                        return None
            # Running the appropriate retriever
            if kwarg['elapse'].seconds != 0:
                df[q] = DataFrame(self._RTFetcher(res['symbol'], res['market'], abs(kwarg['elapse'].days), abs(kwarg['elapse'].seconds)), columns=fields)
                #TODO: Handle only from now, could here reindex df with end value
                #like truncate() which does : df[q] = df[q].ix[kwarg['start']:kwarg['end']]
            else:
                self._logger.info('Fetching historical data from yahoo finance')
                df[q] = DataFrame(self._getHistoricalQuotes(res['symbol'], kwarg['start'], kwarg['end'], kwarg['elapse']), columns=fields)

        return Panel.from_dict(df, intersect=True)

    def _guessResolution(self, start, end):
        #TODO: Find a more subtil, like proportionnale, relation
        elapse = end - start
        if abs(elapse.days) > 5:
            return dt.timedelta(days=elapse.days)
        elif abs(elapse.days) <= 5 and abs(elapse.days) > 1:
            return dt.timedelta(days=elapse.days, hours=1)
        else:
            return dt.timedelta(days=1, minutes=10)

    def _RTFetcher(self, symbol, market, days, freq):
        url = 'http://www.google.com/finance/getprices?q=%s&x=%s&p=%sd&i=%s' % (symbol, market, str(days), str(freq+1))
        self._logger.info('Retrieving data from %s' % url)
        self._logger.info('on %d days with a precision of %d secs' % (days, freq) )
        try:
            page = urllib2.urlopen(url)
        except IOError:
            self._logger.error('** Bad url: %s' %url)
        feed = ''
        data = []
        while (re.search('^a', feed) == None):
            feed = page.readline()
        while ( feed != '' ):
            data.append(np.array(map(float, feed[:-1].replace('a', '').split(','))))
            feed = page.readline()
        dates, open, close, high, low, volume = zip(*data)
        data = {
                'open' : open,
                'close' : close,
                'high' : high,
                'low' : low,
                'volume' : volume
                }
        #dates = Index([self.dateFormat(float(d)) for d in dates])
        index = Index(epochToDate(d) for d in dates)
        return DataFrame(data, index=index)

    def _getHistoricalQuotes(self, symbol, start, end, elapse=None):
        quotes = fin.quotes_historical_yahoo(symbol, start, end)
        dates, open, close, high, low, volume = zip(*quotes)

        data = {
            'open' : open,
            'close' : close,
            'high' : high,
            'low' : low,
            'volume' : volume
        }

        dates = Index([dt.date.fromordinal(int(d)) for d in dates])
        df = DataFrame(data, index=dates)
        #ix method could work too
        if elapse != None:
            keep = list()
            for i in range(0, len(dates)):
                if i % elapse.days == 0: keep.append(i)
            subindex = [dates[i] for i in keep] 
            df = df.reindex(index=subindex)
        return df

    def getSnaphot(self, quotes, **kwarg):   #to be replaced by quotes when database operationnal
        symbols = list()
        markets = list()
        for q in quotes:
            res = self._db.getData('stocks', {'ticker': q}, ("symbol","market"))
            symbols.append(res['symbol'])
            markets.append(res['market'])
        #markets = ['NASDAQ', 'EPA', 'NASDAQ']
        if kwarg['light']:
            snapshot = {q : dict() for q in symbols}
            data = self._lightSummary(symbols, markets)
            i = 0
            for s in symbols:
                snapshot[s] = data[i]
                i += 1
            return snapshot
        else:
            return self._heavySummary(symbols)

    def _lightSummary(self, symbols, markets):
        #TODO: finir de changer les index et comprendre tous les champs
        url = 'http://finance.google.com/finance/info?client=ig&q=%s:%s' % (symbols[0], markets[0])
        for i in range(1, len(symbols)):
            url = url + ',%s:%s' % (symbols[i], markets[i])
        return json.loads(urllib2.urlopen(url).read()[3:], encoding='latin-1')

    def _heavySummary(self, symbols):
        url = 'http://www.google.com/ig/api?stock=' + symbols[0]
        for s in symbols[1:]:
            url = url + '&stock=' + s
        self._logger.info('Retrieving Snapshot from %s' % url)
        try:
            url_fd = urllib2.urlopen(url)
        except IOError:
            self._logger.error('** Bad url: %s' %url)
        try:
            xml_doc = minidom.parse(url_fd)
            root_node = xml_doc.documentElement
        except:
            self._logger.error('** Parsing xml google response')
        i = 0
        snapshot = {q : dict() for q in symbols}
        for node in root_node.childNodes:  #node.Name=finance
            if ( node.nodeName != 'finance' ): continue
            for item_node in node.childNodes:
                if ( item_node.nodeType != Node.ELEMENT_NODE ): continue
                snapshot[symbols[i]][item_node.nodeName] = item_node.getAttribute('data')
            i += 1
        return snapshot


''' Example'''
if __name__ == '__main__':
    print 'Test of the module'

    dataobj = DataAccess('../../dataSubSystem/assets.db')
    startday = dt.datetime(2011,12,6)
    endday = dt.datetime(2012,12,1)
    delta = dt.timedelta(days=4)
    data = dataobj.getQuotes(['google'], ['open', 'volume'], start=startday, end=endday)
    print data['google']['open'].head()
    summary = dataobj.getSnaphot(['google', 'archos'], light=True)
    print 'Google variation: %s' % summary['GOOG'][Alias.VARIATION]

    #dataobj._db.updateStockDb(data)   #TODO: Not functionnal yet

    #TODO: Something more elegant, like automatic closing at destruction
    dataobj._db.finalize()
