import ipdb as pdb
import sys
import os

sys.path.append(str(os.environ['QTRADE']))
from pyTrade.data.DataAgent import DataAgent
from pyTrade.data.QuantDB import Fields

import pandas as pd

import unittest
import datetime as dt
import pytz

''' Way to use:
    python -m unittest --buffer --catch --failfast
    test_data.test_DataAgent.test_connectTo
'''


class test_getQuotes(unittest.TestCase):
    '''
    A test class for the data agent of quanTrade
    '''
    def setUp(self):
        ''' called at the beginning of each test '''
        self.tickers   = ['starbucks']
        self.fields    = ['low', 'adj_close', 'volume']
        self.start     = dt.datetime(2004, 12, 1, tzinfo = pytz.utc)
        self.end       = dt.datetime(2012, 12, 31, tzinfo = pytz.utc)
        self.offset    = pd.datetools.BMonthEnd(4)
        self.timestamp = pd.date_range(self.start, self.end, freq = self.offset)
        self.agent     = DataAgent()
        self.agent.connectTo(['remote', 'database'], db_name='stocks.db', lvl='critical')

    ''' ----------------------------------------------------  Index -----------------------'''
    def test__makeIndex(self):
        kwargs = {'start' : self.start,
                  'end'   : self.end,
                  'delta' : self.offset,
                  'period': pd.datetools.BMonthEnd(6)}

        made_idx = self.agent._makeIndex(kwargs)

        self.assertTrue(isinstance(made_idx, pd.DatetimeIndex))
        self.assertTrue(made_idx.size > 0)
        self.assertTrue(made_idx == self.timestamp)

    def test__guessResolution(self):
        delta = self.agent._guessResolution(self.star, self.end)
        self.assertTrue(isinstance(delta, pd.datetools.DateOffset))
        self.assertTrue(delta == pd.Datetools.BDay())

    ''' ----------------------------------------------------  Remote  ---------------------'''
    def test_getMinutelyQuotes(self):
        symbols = {self.tickers[0]: 'SBUX'}
        markets = {self.tickers[0]: 'NASDAQ'}
        df = self.remote.getMinutelyQuotes(symbols[self.tickers[0], markets[self.tickers[0], self.timestamp]])
        df_fields = pd.DataFrame(df, columns=self.fields)
        cut_df = df.truncate(after=self.timestamp[-1])

    def test_getHistoricalQuotes(self):
        symbols = {self.tickers[0]: 'SBUX'}
        markets = {self.tickers[0]: 'NASDAQ'}
        df = self.remote.getHistoricalQuotes(symbols[self.tickers[0], markets[self.tickers[0], self.timestamp]])
        df_fields = pd.DataFrame(df, columns=self.fields)

    ''' ----------------------------------------------------  Database  -------------------'''
    def test__inspectDB(self):
        db_df, idx_to_dl = self.agent._inspectDB(self.tickers[0], self.timestamp, self.fields)

    def test_getDataIndex(self):
        index = self.db.getDataIndex(self.tickers[0], self.fields, summary=False)

    def test_updateStockDb(self):
        panel = None
        self.db.updateStockDb(panel, Fields.QUOTES, drop=True)

    def test_getQuotesDB(self):
        quotes_db = self.db.getQuotesDB(self.tickers[0], self.timestamp)
        df = pd.DataFrame(quotes_db, columns=self.fields)
        clean_df = df.dropna()
        self.assertTrue(clean_df.index.tzinfo)

    def test_getTickersCode(self):
        symbols, markets = self.db.getTickersCodes(self.tickers)
        self.assertTrue(isinstance(symbols, list) and isinstance(markets, list))
        self.assertTrue(symbols[self.tickers[0]] == 'SBUX')
        self.assertTrue(markets[self.tickers[0]] == 'NASDAQ')

    ''' ----------------------------------------------------  Principal  ------------------'''
    def test_getQuotes_Index(self):
        quotes = self.agent.getQuotes(
                self.tickers,
                self.fields,
                index=self.timestamp,
                save=False,
                reverse=False)
        self.assertTrue(isinstance(quotes[self.tickers[0]][self.fields[0]][5], float))

    def test_getQuotes_Dates(self):
        quotes = self.agent.getQuotes(
                self.tickers,
                self.fields,
                start=self.start,
                end=self.end,
                delta=self.offset,
                save=False,
                reverse=False)
        self.assertTrue(isinstance(quotes[self.tickers[0]][self.fields[0]][5], float))
        pdb.set_trace()

    def tearDown(self):
        if self.agent.connected['database']:
            print('Closing database')
            self.agent.db.close(commit=True)
    #TODO A datetime/timestamp handler, monitor ? inhereting from functions in utils


def build_suite():
    tests = ['test_getQuotes_Index', 'test_getQuotes_Dates']
    return unittest.TestSuite(map(test_DataAgent, tests))

if __name__ == '__main__':
    #unittest.main()
    # Automatci suite build
    #suite = unittest.TestLoader().loadTestsFromTestCase(test_DataAgent)
    # Vs manually
    suite = build_suite()
    unittest.TextTestRunner(verbosity=2).run(suite)
