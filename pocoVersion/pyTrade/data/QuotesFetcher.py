#!/usr/bin/python
# -*- coding: utf8 -*-

import urllib2
import sys, re, time
import re
#import sqlite3 as sql

from pandas import Index, DataFrame
from pandas.core.datetools import BMonthEnd
from pandas import ols

sys.path.append('..')
from Utilities import LogSubSystem
from Utilities import DatabaseSubSystem
#TODO: use above module to handle datbase communication

class QuotesDL(object):
    ''' Quote object - fill everything related:
            name, code, current value, bought value,
            market, actions owned,
            and date, open, close, volume, of asked period'''
    def __init__(self, quote, db_name, logger=None):
        # Logger initialisation
        if logger == None:
          self._logger = LogSubSystem('QuoteDL', "debug").getLog()
        else:
          self._logger = logger

        # Getting quotes info from db
        try:
            self._db = DatabaseSubSystem(db_name, self._logger)
            #tables = self._db.getTables()  #TODO:Check table presence and error handling
            res = self._db.execute('select symbol, market, rss from stocks where ticker=:ticker', {"ticker": quote})

            self.symbol = res['symbol']
            self.market = res['market']
            self.rss_source = res['rss']
            self.rss = 'http://www.google.com/finance/company_news?q=' + self.market + ':' + self.symbol + '&output=rss'
        except:
            self._logger.error('Using database SubSystem')
            self._db.close()
        self.name = quote

    def finalize(self):
        ''' Clean up the download process '''
        self._logger.info('Closing database connection.')
        self._db.execute('commit')
        self._db.close()

    def fetchQuotes(self, days, freq):
        ''' retrieve google finance data asked while initializing
        and store it: Date, open, low, high, close, volume '''
        url = 'http://www.google.com/finance/getprices?q=' + self.symbol + '&x=' + self.market + '&p=' + str(days) + 'd&i=' + str(freq*61)
        self._logger.info('Retrieving data from %s' % url)
        try:
            page = urllib2.urlopen(url)
        except IOError:
            self._logger.error('** Bad url: %s' %url)
            sys.exit(1)
        cpt = 1
        feed = ''
        data = []
        while (re.search('^a', feed) == None):
            feed = page.readline()
        while ( feed != '' ):
            data.append(feed[1:-1].split(','))
            feed = page.readline()
        dates, open, close, high, low, volume = zip(*data)
        data = {
                'open' : open,
                'close' : close,
                'high' : high,
                'low' : low,
                'volume' : volume
                }
        dates = Index([self.epochToDate(float(d)) for d in dates])
        #index = date_range(date.fromtimestamp(float(dates)), periods=1000, freq='M')
        return DataFrame(data, index=dates)

    def epochToDate(self, epoch):
        ''' Convert seconds of epoch time to date POSIXct format %Y-%M-%D %H:%m '''
        return time.strftime("%Y-%m-%d %H:%M", time.localtime(epoch))


    def updateDb(self, quotes):
        ''' store quotes and information '''
        ''' Updating index table '''
        self._logger.info('Updating database...')
        #TODO: Handling data accumulation and compression
        uvariation = 0
        ubegin = quotes.index[0]
        uend = quotes.index[len(quotes)-1]
        uvalue = quotes['close'][uend]
        try:
            self._db.execute('update stocks set value=?, variation=?, begin=?, end=? where ticker=?', (uvalue, uvariation, ubegin, uend, self.name))
            res = self._db.execute('drop table if exists ' + self.name)
            self._db.execute('create table ' + self.name + '(date int, open real, low real, high real, close real, volume int)')
            for i in range(0, len(quotes)):
                raw = (quotes.index[i],
                    quotes['open'][i], 
                    quotes['close'][i], 
                    quotes['high'][i],
                    quotes['low'][i],
                    quotes['volume'][i])
                self._db.execute('insert into ' + self.name + ' values(?, ?, ?, ?, ?, ?)', raw)
        except:
            self._logger.error('While insering new values in database')
            self.finalize()


''' Example
if __name__ == '__main__':
    print 'Test of the module'
    #TODO: Send a tuple of quotes and handle everything
    q = QuotesDL('google', '../../dataSubSystem/assets.db')
    quotes = q.fetchQuotes(3, 30)
    q.updateDb(quotes)
    q.finalize()
'''

#TODO Resolve data problem for 30 days 60minutes
#date = time.strftime("%Y-%m-%d %H:%M", time.localtime(float(infos[0][1:])))    #see %c also and %m
