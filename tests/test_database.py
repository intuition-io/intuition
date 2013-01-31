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
    test_data.test_DataAgent.test_connectTo
'''

class test_DataAgent(unittest.TestCase):
    '''
    A test class for the data agent of quanTrade
    '''
    def setUp(self):
        ''' called at the beginning of each test '''
        self.log_handler = logbook.TestHandler()
        self.log_handler.push_thread()
        self.tickers      = ['google', 'apple', 'starbucks']
        self.fields       = ['close', 'volume']
        self.start        = dt.datetime(2006, 1, 1, tzinfo = pytz.utc)
        self.end          = dt.datetime(2010, 12, 31, tzinfo = pytz.utc)
        self.offset       = pd.datetools.BMonthEnd()


    def tearDown(self):
        self.log_handler.pop_thread()
        if self.agent.connected['database']:
            print('Closing database')
            self.agent.db.close(commit=True)
    #TODO A datetime/timestamp handler, monitor ? inhereting from functions in utils


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
