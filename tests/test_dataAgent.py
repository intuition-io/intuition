import unittest
import datetime as dt

class testDataAgent(unittest.TestCase):
    '''
    A test class for the data agent of quanTrade
    '''
    def setUp(self):
        '''initialization'''
        print('Initializing test suite')
        #TODO logger
        self.tickers = ['google', 'archos']
        self.start = dt.datetime(2000,1,1)
        self.end = dt.datetime(2010,1,1)

    def testFake(self):
        ''' test* functions with just self, are test cases '''
        assert 1 == 1

    def tearDown(self):
        ''' uninitialize function '''
        print('Uninitializing test suite')

if __name__ == '__main__':
    unittest.main()
