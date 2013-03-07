import unittest
import logbook
# http://packages.python.org/Logbook/unittesting.html

import ipdb as pdb
import sys
import os

sys.path.append(str(os.environ['QTRADE']))
from pyTrade.data.datafeed import DataFeed

import pandas as pd
import datetime as dt
import pytz

''' Way to use:
    python -m unittest --buffer --catch --failfast
    test_data.test_mysql.test_connectTo
'''

class test_mysql(unittest.TestCase):
    '''
    A test class for the data agent of quanTrade
    '''
    def setUp(self):
        ''' called at the beginning of each test '''
        self.log_handler = logbook.TestHandler()
        self.log_handler.push_thread()
        self.tickers = ['google', 'apple', 'starbucks']
        self.fields  = ['close', 'volume']

    def test__get_tickers(self):
        feeds   = DataFeed()
        tickers = feeds.random_stocks(6)
        assert(len(tickers) == 6)

    def test__get_quotes(self):
        start = dt.datetime(2006, 1, 1, tzinfo   = pytz.utc)
        end   = dt.datetime(2010, 12, 31, tzinfo = pytz.utc)
        feeds = DataFeed()
        data  = feeds.quotes(tickers, start_date = start, end_date = end)
        assert(data.index.tzinfo)
        assert(isinstance(data, pd.DataFrame))

    def tearDown(self):
        self.log_handler.pop_thread()


def build_suite():
    tests = ['']
    return unittest.TestSuite(map(test_mysql, tests))

if __name__ == '__main__':
    #unittest.main()
    # Automatci suite build
    #suite = unittest.TestLoader().loadTestsFromTestCase(test_mysql)
    # Vs manually
    suite = build_suite()
    unittest.TextTestRunner(verbosity=2).run(suite)
