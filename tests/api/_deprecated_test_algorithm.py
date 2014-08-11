'''
Tests for intuition.api.algorithm
'''

import unittest
from nose.tools import ok_, eq_, nottest
import dna.test_utils
import datetime as dt
from intuition.test_framework import (
    TestAlgorithm,
    build_fake_hybridDataFactory
)


# TODO Test with a manager
class AlgorithmTestCase(unittest.TestCase):

    def setUp(self):
        dna.test_utils.setup_logger(self)
        self.today = dt.datetime.today()
        self.past_date = self.today - dt.timedelta(days=10)
        self.test_properties = {'test': True}
        self.algo = TestAlgorithm(properties=self.test_properties)
        self.default_identity = 'johndoe'

    def tearDown(self):
        dna.test_utils.teardown_logger(self)

    @nottest
    def _check_algorithm_object(self, algo):
        self.assertTrue(algo.initialized)
        self.assertFalse(algo._warmed)
        self.assertIsNotNone(algo.sim_params)
        eq_(algo.sids, [])
        eq_(algo.middlewares, [])
        eq_(algo.sources, [])
        eq_(algo.capital_base, 100000.0)

    def test_new_algorithm(self):
        self.assertIsNone(self.algo.manager)
        self._check_algorithm_object(self.algo)

    def test_new_algorithm_without_properties(self):
        algo = TestAlgorithm()
        eq_(algo.identity, self.default_identity)

    def test_overload_initialize(self):
        eq_(self.algo.properties, self.test_properties)

    def test_run_algorithm(self):
        results = self.algo.run(build_fake_hybridDataFactory())
        ok_(not results.empty)

    def test_warm_overload(self):
        pass
