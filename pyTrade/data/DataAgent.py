#!/usr/bin/python
# -*- coding: utf8 -*-

import urllib2
import sys, re, time, os
import datetime as dt
import pytz

import pandas as pd
from pandas import Index, Series, DataFrame, Panel

import numpy as np
import matplotlib.finance as finance

from xml.dom import minidom, Node
import json

sys.path.append(str(os.environ['QTRADEPYTHON']))
from utils.LogSubsystem import LogSubsystem
from QuantDB import QuantSQLite, yahooCode, Fields
from utils.utils import epochToDate

#TODO: Uniform Quote dict structure to implement (and fill in different methods)
#tmp
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

    def getQuotes(self, tickers, fields, index=None, *args, **kwargs):
        ''' 
        @summary: retrieve google finance data asked while initializing
        and store it: Date, open, low, high, close, volume 
        @param quotes: list of quotes to fill
        @param fields: list of fields to store per quotes
        @param index: pandas.Index object, used for dataframes
        @param args: unuse
        @param kwargs.start: date or datetime of the first values
               kwargs.end: date or datetime of the last value
               kwargs.delta: datetime.timedelta object, period of time to fill
               kwargs.save: save to database downloaded quotes
               kwargs.reverse: reverse companie name and field in panel data structure
        @param reverse: fields as columns, comapnies as index
        @return a panel/dataframe/timeserie like closeAt9 = data['google'][['close']][date]
        '''
        save = kwargs.get('save', False)
        reverse = kwargs.get('reverse', False)
        if index != None:
            start_day = index[0]
            end_day = index[len(index)-1]
            delta = index[1] - index[0]  #timedelta object ?
        else:
            start_day = kwargs.get('start', None)
            end_day = kwargs.get('end', pd.datetime.now())
            if start_day != None:
                delta = kwargs.get('delta', self._guessResolution(start_day, end_day))
            else:
                delta = kwargs.get('delta', None)
            if start_day == None and delta != None:
                start_day = end_day - delta
            elif start_day == None and delta == None:
                #TODO: today with a minute precision
                self._logger.error('** Neither index, start, end or elapse (or just end) parameters provided')
                return None
        #TODO: multithread !
        df = dict()
        symbols, markets = self._db.getTickersCodes(tickers)
        for ticker in tickers:
            downloaded = False
            self._logger.info('Processing {} stock'.format(ticker))
            self._logger.info('Inspecting database.')
            #TODO: identificate NaN columns, that will erase everything at dropna() time
            first_db_date, last_db_date, db_freq = self._db.getDataIndex(ticker, summary=True)
            self._logger.debug('Requested delta: {} vs db one available: {}'.format(delta, db_freq))
            if db_freq > delta or db_freq == None:
                self._logger.info('Superior asked frequency, dropping and downloading along whole timestamp')
            elif first_db_date > end_day:
                self._logger.info('No quotes available in database, downloading along whole timestamp')
            else:
                downloaded = True
                if first_db_date > start_day and last_db_date < end_day:
                    self._db.getQuotesDB(ticker, first_db_date, last_db_date, delta)
                    db_df = DataFrame(dataobj._db.getQuotesDB(ticker, start=startday, \
                            end=endday, delta=2 * pd.datetools.Day()), columns=fields).dropna()
                    #TODO: Two different timestamps to download !
                    #to dl: start_day -> first_db_date and last_db_date -> end_day
                elif first_db_date > start_day and last_db_date > end_day:
                    db_df = DataFrame(self._db.getQuotesDB(ticker, start=first_db_date, \
                            end=end_day, delta=delta), columns=fields).dropna()
                    #to dl: start_day -> first_db_date 
                    end_day = first_db_date
                elif first_db_date < start_day and last_db_date < end_day:
                    db_df = DataFrame(self._db.getQuotesDB(ticker, start=start_day, \
                            end=last_db_date, delta=delta), columns=fields).dropna()
                    #last_db_date -> end_day
                    start_day = last_db_date
                elif first_db_date < start_day and last_db_date > end_day:
                    self._logger.info('Quotes available offline, in database')
                    df[ticker] = DataFrame(self._db.getQuotesDB(ticker, start=start_day, \
                            end=end_day, delta=delta), columns=fields).dropna()
                    continue

            self._logger.info('Downloading missing data, from {} to {}'.format(start_day, end_day))
            # Running the appropriate retriever
            if delta.seconds != 0:
                network_df = DataFrame(self._RTFetcher(symbols[ticker], markets[ticker], \
                        abs(delta.days), abs(delta.seconds)), columns=fields)
                network_df.truncate(after=end_day)
                #NOTES like truncate() which does : df[q] = df[q].ix[start_day:end_day]
            else:
                self._logger.info('Fetching historical data from yahoo finance')
                network_df = DataFrame(self._getHistoricalQuotes(symbols[ticker], \
                        start_day, end_day, delta), columns=fields)
            if downloaded:
                self._logger.debug('Checking db index ({}) vs network index ({})'.format(db_df.index[0], network_df.index[0]))
                #if db_df.index[0] > network_df.index[0]: 
                    #df[ticker] = pd.concat([network_df, db_df])
                #else:
                df[ticker] = pd.concat([db_df, network_df]).sort_index()
            else:
                df[ticker] = network_df

        data = Panel.from_dict(df, intersect=True)
        if save:
            #TODO: accumulation and compression of data issue, drop always true at the moment
            self._db.updateStockDb(data, Fields.QUOTES, drop=True)  
        if reverse:
            return Panel.from_dict(df, intersect=True, orient='minor')
        return data
        

    def _guessResolution(self, start, end):
        #TODO: Find a more subtil, like proportional, relation
        elapse = end - start
        if abs(elapse.days) > 5:
            delta = dt.timedelta(days=1)
        elif abs(elapse.days) <= 5 and abs(elapse.days) > 1:
            delta = dt.timedelta(days=1, hours=1)
        else:
            delta = dt.timedelta(days=1, minutes=10)
        self._logger.info('Automatic delta fixing: {}'.format(delta))
        return delta

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
        index = Index(epochToDate(d) for d in dates)
        df.index = df.index.tz_localize(pytz.utc)
        return DataFrame(data, index=index)

    #NOTES: adjusted close ?
    def _getHistoricalQuotes(self, symbol, start, end, elapse=None, adj_flag=False):
        quotes = finance.quotes_historical_yahoo(symbol, start, end, adjusted=adj_flag)

        dates, open, close, high, low, volume = zip(*quotes)
        data = {
            'open' : open,
            'close' : close,
            'high' : high,
            'low' : low,
            'volume' : volume
        }

        dates = Index([pd.datetime.fromordinal(int(d)) for d in dates])
        df = DataFrame(data, index=dates)
        #ix method could work too
        if elapse != None:
            keep = list()
            for i in range(len(dates)):
                if i % elapse.days == 0: keep.append(i)
            subindex = [dates[i] for i in keep] 
            df = df.reindex(index=subindex)
            df.index = df.index.tz_localize(pytz.utc)
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
    dataobj = DataAgent('stocks.db')        # Just needs the relative path to Database directory
    startday = pd.datetime(2011,6,20)      #in db: 2011-12-05
    endday = pd.datetime(2012,4,1)          #in db: 2012-6-1
    delta = dt.timedelta(days=3)            #in db: 1
    data = dataobj.getQuotes(['altair'], ['open', 'volume'], \
            start=startday, end=endday, delta=delta)
    print('================\n{}'.format(data['altair']['open'].head()))
    #summary = dataobj.getSnaphot(['google', 'apple'], light=true)
    #print '(light) Google variation: %s' % summary['google'][Alias.VARIATION]
    #summary = dataobj.getSnaphot(['google', 'apple'], light=False)
    #print '(heavy) Apple market cap: %s' % summary['apple']['market_cap']

    #dataobj._db.updateStockDb(data, Fields.QUOTES, drop=True)  
    #first_date, last_date, freq = dataobj._db.getDataIndex('google', summary=True)
    #print('Data from {} to {} with an interval of {}'.format(first_date, last_date, freq))
    #quotes = DataFrame(dataobj._db.getQuotesDB('google', start=startday,\
            #end=endday, delta=delta), columns=['open', 'volume']).dropna()
    #print quotes.head()
    dataobj._db.close(commit=True)
