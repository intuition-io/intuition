import ipdb as pdb

import sys
import os

import sqlite3 as sql
import numpy as np
from pandas import DataFrame

sys.path.append(str(os.environ['QTRADEPYTHON']))
from utils.DatabaseSubsystem import SQLiteWrapper
from utils.LogSubsystem import LogSubsystem
from utils.decorators import *
from utils.utils import *


class QuantSQLite(SQLiteWrapper):
    #NOTE @singleton
    """
    Specific database facilities for quanTrade software
    """
    def __init__(self, db_file='stocks.db', timezone=pytz.utc,
                 logger=None, lvl='debug'):
        self.tz = timezone
        if logger is None:
            self._logger = LogSubsystem(self.__class__.__name__, lvl).getLog()
        else:
            self._logger = logger
        dbRootDir = os.environ['QTRADEDATA']
        db_file = '/'.join((dbRootDir, db_file))
        SQLiteWrapper.__init__(self, db_file, self._logger)

    #TODO: code that !
    @deprecated
    def findDB(self, dbName):
        ''' search database specified in QuanTrade directories '''

    def getTickersCodes(self, tickers):
        ''' simple function often used '''
        if self._db_name.find('stocks.db') == -1:
            self._logger.error('** Bad DB, You are not connected to stocks.db')
            return None, None
        symbols = dict()
        markets = dict()
        table = 'properties'
        fields = ('symbol', 'market')
        for t in tickers:
            selector = {'ticker': t}
            res = self.getData(table, selector, fields)
            if res is None:
                self._logger.warning('No references found in database.')
                continue
            symbols[t] = res[fields[0]]
            markets[t] = res[fields[1]]
        return symbols, markets

    def updateStockDb(self, quotes, fields, drop=False):
        '''
        @summary store quotes and information in SQLiteDB
        @param quotes: pandas.Panel not reversed,
                       like quotes[companies][fields]
        '''
        #pdb.set_trace()
        #TODO: maybe a general update function ?
        self._logger.info('Updating database...')
        #TODO: Handling data accumulation and compression, right now just drop
        for name, frame in quotes.iteritems():
            self._logger.info('saving {} quotes'.format(name))
            for item in fields:
                if item not in frame.columns:
                    frame[item] = np.empty(len(frame.index))
                    frame[item].fill(np.NaN)
            try:
                if drop:
                    self.execute('drop table if exists ' + name)
                    self.execute('create table ' + name +
                                 '(date int, {} real, {} real, {} real,\
                                 {} real, {} int, {} real)'
                                 .format(*Fields.QUOTES))
                #NOTE: could it be possible in one line with executemany ?
                frame = frame.fillna(-1)
                #frame = frame.fillna(method='pad')
                #frame = frame.dropna()
                for i in range(len(frame.index)):
                    raw = (dateToEpoch(frame.index[i]),
                           frame['open'][i],
                           frame['close'][i],
                           frame['high'][i],
                           frame['low'][i],
                           frame['volume'][i],
                           frame['adj_close'][i])
                    self.execute('insert into ' + name +
                                 ' values(?, ?, ?, ?, ?, ?, ?)', raw)
            except:
                self._logger.error('While insering new values in database')
                return 1
        return 0

    def getDataIndex(self, ticker, fields=None, summary=True):
        '''
        @summary retrieve the ticker data index from db,
                 for storage optimization
        @return a pandas.Index
        '''
        assert isinstance(ticker, str)
        if not self.isTableExists(ticker):
            self._logger.warning('Table does not exist')
            return None, None, None
        self._logger.info('Getting index quotes properties.')
        try:
            dates = self.execute('select date from {}'.format(ticker))
        except sql.Error, e:
            self._logger.error('** While getting index: {}'.format(e.args[0]))
            return None
        if len(dates) < 2 or not isinstance(dates[0][0], int):
            return None
        if isinstance(fields, list):
            selector = {'date': dates[0][0]}
            res = self.getData(ticker, selector, fields)
            if not res:
                self._logger.error('** No data index found in database about {}'.format(ticker))
                return None
            #FIXME res is sometime a float, sometime a list
            for value in res:
                if not value:
                    #TODO may be keep available fields and pop the others
                    return None
        if summary:
            oldest_date = epochToDate(dates[0][0], self.tz)
            latest_date = epochToDate(dates[-1][0], self.tz)
            freq = epochToDate(dates[1][0], self.tz) - oldest_date
            self._logger.debug('Data from {} to {} with an interval \
                                of {} days, {}mins'
                .format(oldest_date, latest_date,
                        freq.days, freq.seconds / 60))
            return [oldest_date, latest_date, freq]
        else:
            dates = [epochToDate(dates[i][0]) for i in range(len(dates))]
            return dateToIndex(dates, self.tz)
            #return Index([dates-dt.timedelta(hours=23) for dates in index
                          #if index[0].hour == 23]).tz_localize(self.tz)

    def getQuotesDB(self, ticker, index):
        '''
        @summary like network utilities, it gets from db data according params
        @params see getData
        @return a dataframe, still for other DataAgent functions compatibility
        '''
        assert (isinstance(index, pd.Index))
        assert (index.size > 0)
        if not index.tzinfo:
            index = index.tz_localize(self.tz)
        self._logger.info('Retrieving {} quotes from database'.format(ticker))
        db_dates = self.getDataIndex(ticker, summary=False)
        if isinstance(db_dates, pd.DatetimeIndex):
            #NOTE: Something more generic ?
            self._logger.debug('Query: select {} from {}'
                .format(' ,'.join(Fields.QUOTES), ticker))
            #FIXME cut the last element because of indexing
            res = self.execute('select {} from {}'
                    .format(' ,'.join(Fields.QUOTES), ticker))
            #TODO Handle dirty missed
            print('Res: {}, dates: {}'.format(len(res), db_dates.size))
            assert(len(res) == db_dates.size)
            df = DataFrame.from_records(res, index=db_dates,
                                        columns=Fields.QUOTES)
            return reIndexDF(df, start=index[0], end=index[-1],
                             delta=index.freq)
        return None


#TODO: Same for google json and xml retrievig
googleCode = dict()

#TODO: codes for non-us markets are different. Like JXR.PA for archos
#TODO: Tester, comprendre, et reformater ces valeurs
yahooCode = {'ask':'a', 'average daily volume':'a2', 'ask size':'a5',
        'bid':'b', 'ask rt':'b2', 'bid rt':'b3', 'dividend yield':'y',
        'book value':'b4', 'bid size':'b6', 'change and percent': 'c',
        'change':'c1', 'commission':'c3', 'change rt':'c6',
        'after hours change rt':'c8', 'dividend':'d', 'last trade date':'d1',
        'trade date':'d2', 'earnings':'e', 'error':'e1',
        'eps estimate year':'e7', 'eps estimate next year':'e8', 'eps estimate next quarter':'e9',
        'float shares':'f6', 'day low':'g', 'day high':'h',
        '52-week low':'j', '52-week high':'k', 'holdings gain percent':'g1',
        'annualized gain':'g3', 'holdings gain':'g4', 'holdings gain percent rt':'g5',
        'holdings gain rt':'g6', 'more info':'i', 'order book rt':'i5',
        'market capitalization':'j1', 'market cap rt':'j3', 'EBITDA':'j4',
        'change from 52-week':'j5', 'percent change from 52-week low':'j6', 'last trade rt with time':'k1',
        'change percent rt':'k2', 'last trade size':'k3', 'change from 52-week high':'k4',
        'percebt change from 52-week high':'k5', 'last trade with time':'l', 'last trade price':'l1',
        'high limit':'l2', 'low limit':'l3', 'day range':'m',
        'day range rt':'m2', '50-day ma':'m3', '200-day ma':'m4',
        'percent change from 50-day ma':'m8', 'name':'n', 'notes':'n4',
        'open':'o', 'previous close':'p', 'price paid':'p1',
        'change percent':'p2', 'price/sales':'p5', 'price/book':'p6',
        'ex-dividend date':'q', 'p/e ratio':'r', 'dividend date':'r1',
        'p/e ratio rt':'r2', 'peg ratio':'r5', 'price/eps estimate year':'r6',
        'price/eps estimate next year':'r7', 'symbol':'s', 'shares owned':'s1',
        'short ratio':'s7', 'last trade time':'t1', 'trade links':'t6',
        'ticker trend':'t7', '1 year target price':'t8', 'volume':'v',
        'holdings value':'v1', 'holdings value rt':'v7', '52-week range':'w',
        'day value change':'w1', 'day value change rt':'w4', 'stock exchange':'x'}


class Fields:
    QUOTES = ['open', 'low', 'high', 'close', 'volume', 'adj_close']


'''
if __name__ == '__main__':
    db = QuantSQLite('stocks.db')
    #print db.execute('select sqlite_version()')
    db.queryFromScript('buildStocks.sql')
    db.close()
'''
