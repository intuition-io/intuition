import ipdb as pdb
import sys
import os

sys.path.append(str(os.environ['QTRADE']))
from pyTrade.data.DataAgent import DataAgent

import pandas as pd

import unittest
import datetime as dt
import pytz

''' Way to use:
    python -m unittest --buffer --catch --failfast
    test_data.test_DataAgent.test_connectTo
'''

#TODO SQLite class -> QuantDB.py
#                  -> DatabaseSubsystem


class test_DataAgent(unittest.TestCase):
    '''
    A test class for the data agent of quanTrade
    '''
    def setUp(self):
        ''' called at the beginning of each test '''
        self.tickers      = ['starbucks']
        self.fields       = ['low', 'adj_close', 'volume']
        self.start        = dt.datetime(2004, 12, 1, tzinfo = pytz.utc)
        self.end          = dt.datetime(2012, 12, 31, tzinfo = pytz.utc)
        self.offset       = pd.datetools.BMonthEnd(4)
        self.simple_agent = DataAgent()

    def test_connectToRemote(self):
        ''' DataAgent sources controller, make up connections with their initialisations '''
        self.simple_agent.connectTo(['remote'], timezone=pytz.utc, level='info')
        self.assertTrue(self.simple_agent.connected['remote'])

    def test_connectToDB(self):
        self.simple_agent.connectTo(['database'], db_name='stocks.db')
        self.assertTrue(self.simple_agent.connected['database'])

    def test_getQuotes_Index(self):
        timestamp = pd.date_range(self.start, self.end, freq=self.offset)
        self.simple_agent.connectTo(['remote', 'database'], db_name='stocks.db',
                                    lvl='critical')
        quotes = self.simple_agent.getQuotes(
                self.tickers,
                self.fields,
                index=timestamp,
                save=False,
                reverse=False)
        self.assertTrue(isinstance(quotes[self.tickers[0]][self.fields[0]][5], float))

    def test_getQuotes_Dates(self):
        self.simple_agent.connectTo(['remote', 'database'], db_name='stocks.db', lvl='critical')
        quotes = self.simple_agent.getQuotes(
                self.tickers,
                self.fields,
                start=self.start,
                end=self.end,
                delta=self.offset,
                save=False,
                reverse=False)
        self.assertTrue(isinstance(quotes[self.tickers[0]][self.fields[0]][5], float))
        pdb.set_trace()

    def test__guessResolution(self):
        pass

    def test_help(self):
        self.simple_agent.help('test')

    def tearDown(self):
        if self.simple_agent.connected['database']:
            print('Closing database')
            self.simple_agent.db.close(commit=True)
    #TODO A datetime/timestamp handler, monitor ? inhereting from functions in utils


class test_RemoteData(unittest.TestCase):
    ''' Class used by DataAgent to fetch data from the web '''
    def setUp(self):
        pass

    def test_init(self):
        pass

    def test_getMinutelyQuotes(self):
        pass

    def test_getHistoricalQuotes(self):
        pass

    def test_getStockSnapshot(self):
        pass

    def test__lightSummary(self):
        pass

    def test__heavySummary(self):
        pass

    def test_getStockInfo(self):
        pass

    def tearDown(self):
        pass


def build_suite():
    tests = ['test_connectTo', 'test_getQuotes']
    return unittest.TestSuite(map(test_DataAgent, tests))

if __name__ == '__main__':
    #unittest.main()
    # Automatci suite build
    #suite = unittest.TestLoader().loadTestsFromTestCase(test_DataAgent)
    # Vs manually
    suite = build_suite()
    unittest.TextTestRunner(verbosity=2).run(suite)
