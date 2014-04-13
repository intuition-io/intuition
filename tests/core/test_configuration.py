'''
Tests for intuition.core.configuration
'''

import unittest
from nose.tools import raises
import intuition.test_utils as test_utils
import pandas as pd
import intuition.core.configuration as configuration
from dna.errors import DynamicImportFailed
from intuition.errors import InvalidConfiguration


class ConfigurationUtilsTestCase(unittest.TestCase):

    def test_logfile(self):
        logfile = configuration.logfile('fake_id')
        self.assertIn('.intuition/logs/fake_id.log', logfile)


class ContextLoadTestCase(unittest.TestCase):

    def setUp(self):
        test_utils.setup_logger(self)
        self.good_driver = \
            'intuition.test_utils.FakeContext://localhost/path?valid=true'
        self.bad_driver = \
            'no.file.FileContext://localhost/path?valid=true'
        self.bad_config = \
            'intuition.test_utils.FakeContext://localhost/path?valid=false'
        self.bad_formatted_config = \
            'intuition.test_utils.FakeContext://localhost/path?format=false'

    def tearDown(self):
        test_utils.teardown_logger(self)

    def test_load_context(self):
        with configuration.Context(self.good_driver) as context:
            self.assertIsInstance(context, dict)
            self.assertIsInstance(context['strategy'], dict)
            self.assertIsInstance(context['config'], dict)

    @raises(InvalidConfiguration)
    def test_validate_bad_config(self):
        bad_config = {}
        ctx = configuration.Context(self.bad_driver)
        ctx._validate(bad_config)

    def test_validate_good_config(self):
        good_config = {
            'universe': 'nasdaq,4',
            'index': pd.date_range('2014/2/3', periods=30),
            'modules': {
                'algorithm': 'dualma'
            }
        }
        ctx = configuration.Context(self.bad_driver)
        self.assertIsNone(ctx._validate(good_config))

    @raises(InvalidConfiguration)
    def test_load_bad_configuration(self):
        ctx = configuration.Context(self.bad_formatted_config)
        ctx.__enter__()

    def test_loaded_configuration(self):
        with configuration.Context(self.good_driver) as context:
            for field in ['manager', 'algorithm', 'data']:
                self.assertIn(field, context['strategy'])
            for field in ['index', 'live']:
                self.assertIn(field, context['config'])

    @raises(DynamicImportFailed)
    def test_absent_driver_context_load(self):
        ctx = configuration.Context(self.bad_driver)
        ctx.__enter__()
