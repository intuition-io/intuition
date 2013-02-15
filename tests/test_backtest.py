import unittest
import logbook

import ipdb as pdb
import sys
import os

sys.path.append(os.environ['QTRADE'])
from pyTrade.compute.engine import Simulation
from pyTrade.ai.manager import PortfolioManager

import json

''' Way to use:
    python -m unittest --buffer --catch --failfast
    test_data.test_DataAgent.test_connectTo
'''


class test_backtest(unittest.TestCase):
    '''
    A test class for the data agent of quanTrade
    '''
    def setUp(self):
        self.log_handler = logbook.TestHandler()
        self.log_handler.push_thread()
        self.bt_path = '{}/backtester'.format(os.environ['QTRADE'])

    def test__read_config(self):
        algo_name = 'Momentum'
        algo_cfg  = json.load(open('{}/algos.cfg'.format(self.bt_path), 'r'))[algo_name]
        assert(isinstance(algo_cfg['debug'], int))
        assert(isinstance(algo_cfg['window_length'], int))
        manager_name = 'OptimalFrontier'
        manager_cfg  = json.load(open('{}/managers.cfg'.format(self.bt_path), 'r'))[manager_name]
        assert(isinstance(manager_cfg['max_weight'], float) or isinstance(manager_cfg['max_weight'], int))
        assert(isinstance(manager_cfg['source'], unicode))

        bt_cfg      = {'algorithm' : 'Momentum', 'manager'   : 'Equity', 'level' : 'debug',
                        'tickers'   : 'random,1', 'start' : '2005-01-10', 'end'     : '2010-07-03', 'interactive' : True}
        algo_cfg    = {'debug'     : 1, 'window_length'      : 3}
        manager_cfg = {'source'    : 'mysql', 'max_weight'   : 0.6, 'loopback' : 60}
        engine = Simulation()
        args = engine.read_config(bt_cfg=bt_cfg, a_cfg=algo_cfg, m_cfg=manager_cfg)

    def test__run_backtest(self):
        engine = Simulation()
        #engine.backtest_cfg = {'algorithm' : 'Momentum', 'manager'   : 'Equity', 'level' : 'debug',
                               #'tickers'   : 'google,apple', 'start' : '2005-01-10', 'end'     : '2010-07-03', 'interactive' : True}
        #engine.algo_cfg     = {'debug'     : 1, 'window_length'      : 3}
        #engine.manager_cfg  = {'source'    : 'mysql', 'max_weight'   : 0.6, 'loopback'   : 60}
        bt_cfg      = {'algorithm' : 'Momentum', 'manager'   : 'Equity', 'level' : 'debug',
                        'tickers'   : 'random,1', 'start' : '2005-01-10', 'end'     : '2010-07-03', 'interactive' : True}
        algo_cfg    = {'debug'     : 1, 'window_length'      : 3}
        manager_cfg = {'source'    : 'mysql', 'max_weight'   : 0.6, 'loopback' : 60}
        engine = Simulation()
        args = engine.read_config(bt_cfg=bt_cfg, a_cfg=algo_cfg, m_cfg=manager_cfg)
        results = engine.runBacktest()

    def test__get_results(self):
        engine = Simulation()
        assert(engine is not None)
        risks = engine.overall_metrics(db_id='test', save=False)
        assert(isinstance(risks['Sharpe.Ratio'], float))
        assert(isinstance(risks['Volatility'], float))

    def tearDown(self):
        self.log_handler.pop_thread()


class test_zipline(unittest.TestCase):
    '''
    To test my custom use of zipline
    '''
    def setUp(self):
        pass

    def test__init(self):
        pass

    def test__run(self):
        pass

    def tearDown(self):
        pass


class test_manager(unittest.TestCase):
    '''
    To test decisions made by the manager
    '''
    def setUp(self):
        pass

    def test__setup(self):
        manager = PortfolioManager(0.02)
        assert(manager)
        manager.setup_strategie('Equity', {'max_weight': 0.8})
        #NOTE manager.update is touch to test

    def test__signals_handler(self):
        manager = PortfolioManager()
        order_book = manager.trade_signals_handler({'goog': -532.12, 'aaple': 723.23})

    def tearDown(self):
        pass


def build_suite():
    tests = ['test__read_config', 'test__run_backtest']
    return unittest.TestSuite(map(test_backtest, tests))

if __name__ == '__main__':
    #unittest.main()
    ## Automatci suite build
    #suite = unittest.TestLoader().loadTestsFromTestCase(test_DataAgent)
    ## Vs manually
    suite = build_suite()
    unittest.TextTestRunner(verbosity=2).run(suite)
