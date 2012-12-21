#!/usr/bin/python
# -*- coding: utf8 -*-

import urllib2
import sys, re, time, os
import datetime as dt

from pandas import Index, Series, DataFrame, Panel

import numpy as np
import matplotlib.finance as fin

from xml.dom import minidom, Node
import json

sys.path.append(str(os.environ['QTRADEPYTHON']))
from utils.LogSubsystem import LogSubsystem
from QuantDB import QuantSQLite, yahooCode
from utils.utils import epochToDate

#TODO: Uniform Quote dict structure to implement (and fill in different methods)

class Alias (object):
    SYMBOL = 't'
    MARKET = 'e'
    VALUE = 'l'
    DATE = 'lt'
    VARIATION = 'c'
    VAR_PER_CENT = 'cp'


class DataAgent(object):
    ''' Quote object - fill everything related:
            name, code, current value, bought value,
            market, actions owned,
            and date, open, close, volume, of asked period'''
    # Handling different sources like in QSTK ?
    def __init__(self, db_location=None, logger=None):
        # Logger initialisation
        if logger == None:
          self._logger = LogSubsystem(DataAgent.__name__, "debug").getLog()
        else:
          self._logger = logger
        #TODO: Trouver ici la database, boulot du prochain module
        if db_location != None:
            self._db = QuantSQLite(db_location)
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
        @param reverse: fields as columns, comapnies as index
        @return a panel/dataframe/timeserie like closeAt9 = data['google'][['close']][date]
        '''
        if index != None:
            kwarg['start'] = index[0]
            kwarg['end'] = index[len(index)-1]
            kwarg['elapse'] = index[1] - index[0]  #timedelta object ?
        else:
            if not kwarg.has_key('end'):
                kwarg['end'] = dt.datetime.now()
            if kwarg.has_key('start'):
                if not kwarg.has_key('elapse'):
                    kwarg['elapse'] = self._guessResolution(kwarg['start'], kwarg['end'])
            elif not kwarg.has_key('start'):
                if kwarg.has_key('elapse'):
                    kwarg['start'] = kwarg['end'] - kwarg['elapse']
                else:
                    #TODO: today with a minute precision
                    self._logger.error('** Neither start, end or elapse parameters provided')
                    return None
        #TODO: multithread !
        df = dict()
        i = 0
        symbols, markets = self._db.getTickersCodes(quotes)
        for q in quotes:
            self._logger.info('Processing %s stock' % q)
            # Compute start, end, elapse, whatever the parameters
            #NOTE: Compute instead an index used for every function ?
            # Running the appropriate retriever
            if kwarg['elapse'].seconds != 0:
                df[q] = DataFrame(self._RTFetcher(symbols[i], markets[i], abs(kwarg['elapse'].days), abs(kwarg['elapse'].seconds)), columns=fields)
                #TODO: Handle only from now, could here reindex df with end value
                #like truncate() which does : df[q] = df[q].ix[kwarg['start']:kwarg['end']]
            else:
                self._logger.info('Fetching historical data from yahoo finance')
                df[q] = DataFrame(self._getHistoricalQuotes(symbols[i], kwarg['start'], kwarg['end'], kwarg['elapse']), columns=fields)
            i += 1

        if kwarg.has_key('reverse'):
            if kwarg['reverse']:
                return Panel.from_dict(df, intersect=True, orient='minor')
        return Panel.from_dict(df, intersect=True)

    def _guessResolution(self, start, end):
        #TODO: Find a more subtil, like proportional, relation
        elapse = end - start
        if abs(elapse.days) > 5:
            return dt.timedelta(days=1)
        elif abs(elapse.days) <= 5 and abs(elapse.days) > 1:
            return dt.timedelta(days=1, hours=1)
        else:
            return dt.timedelta(days=1, minutes=10)

    def _RTFetcher(self, symbol, market, days, freq):
        params = urllib2.urlencode({'q': symbol, 'x': market, 'p': str(days)+d, 'i': str(freq+1)})
        url = 'http://www.google.com/finance/getprices?q=%s&x=%s&p=%sd&i=%s' % (symbol, market, str(days), str(freq+1))
        self._logger.info('on %d days with a precision of %d secs' % (days, freq) )
        try:
            page = urllib2.urlopen(url)
        except urllib2.HTTPError:
            self._logger.error('** Unable to fetch data for stock: %s'.format(symbol))
            return None
        except urllib2.URLError:
            self._logger.error('** URL error for stock: %s'.format(symbol))
            return None
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

    #TODO: adjusted close ?
    def _getHistoricalQuotes(self, symbol, start, end, elapse=None, adj_flag=False):
        quotes = fin.quotes_historical_yahoo(symbol, start, end, adjusted=adj_flag)

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

    def getSnaphot(self, tickers, light=True):
        symbols, markets = self._db.getTickersCodes(tickers)
        snapshot = {q : dict() for q in tickers}
        if light:
            data = self._lightSummary(symbols, markets)
        else:
            data = self._heavySummary(symbols)
        i = 0
        for item in tickers:
            snapshot[item] = data[i]
            i += 1
        return snapshot

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
        #snapshot = {q : dict() for q in symbols}
        snapshot = list()
        ticker_data = dict()
        for node in root_node.childNodes:  #node.Name=finance
            if ( node.nodeName != 'finance' ): continue
            ticker_data.clear()
            for item_node in node.childNodes:
                if ( item_node.nodeType != Node.ELEMENT_NODE ): continue
                ticker_data[item_node.nodeName] = item_node.getAttribute('data')
            i += 1
            snapshot.append(ticker_data)
        return snapshot

    #TODO: a separate class with functions per categories of data
    #NOTE: The YQL can fetch this data (http://www.yqlblog.net/blog/2009/06/02/getting-stock-information-with-%60yql%60-and-open-data-tables/)
    def financeRequest(self, quotes, fields):
        #TODO: checking if field is in yahooCode
        #TODO: remove " from results
        symbols, markets = self._db.getTickersCodes(index, quotes)
        fields.append('error')
        url = 'http://finance.yahoo.com/d/quotes.csv?s='
        url = url + '+'.join(symbols) + '&f='
        code = list()
        url += ''.join([yahooCode[item.lower()] for item in fields])
        data = urllib2.urlopen(url)
        df = dict()
        for item in symbols:
            #FIXME: ask size return different length arrays !
            df[item] = Series(data.readline().strip().strip('"').split(','), index=fields)
        return DataFrame(df)


    def help(self, category):
        #TODO: stuff to know like fields and functions
        print('{} help'.format(category))


''' Example'''
if __name__ == '__main__':
    dataobj = DataAgent('stocks.db')   # Just needs the relative path to Database directory
    startday = dt.datetime(2011,12,6)
    endday = dt.datetime(2012,12,1)
    delta = dt.timedelta(days=4)
    data = dataobj.getQuotes(['altair', 'google'], ['open', 'close', 'high'], start=startday, end=endday)
    print data['altair']['open'].head()
    #summary = dataobj.getSnaphot(['google', 'apple'], light=False)
    #print 'Google variation: %s' % summary['google'][Alias.VARIATION]
    #print 'Google market cap: %s' % summary['google']['market_cap']

    dataobj._db.updateStockDb(data)   #TODO: Not functionnal yet

    dataobj._db.commit(close=True)
