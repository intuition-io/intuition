'''
Tests for intuition.core.configuration
'''

import unittest
from nose.tools import raises
import pytz
import dna.test_utils as test_utils
import pandas as pd
import schematics
import intuition.core.configuration as configuration
from dna.errors import DynamicImportFailed
from intuition.errors import InvalidConfiguration


class ConfigurationUtilsTestCase(unittest.TestCase):

    def test_logfile(self):
        logfile = configuration.logfile('fake_id')
        if 'tmp' in logfile:
            self.assertEqual('/tmp/logs/fake_id.log', logfile)
        else:
            self.assertIn('.intuition/logs/fake_id.log', logfile)


class ContextLoadTestCase(unittest.TestCase):

    def setUp(self):
        test_utils.setup_logger(self)
        self.good_driver = \
            'intuition.test_framework.FakeContext://localhost/path?valid=true'
        self.bad_driver = \
            'no.file.FileContext://localhost/path?valid=true'
        self.bad_config = \
            'intuition.test_framework.FakeContext://localhost/path?valid=false'
        self.bad_formatted_config = '{}://localhost/{}'.format(
            'intuition.test_framework.FakeContext', 'path?format=false')
        self.bad_formatted_driver = 'whatever'

    def tearDown(self):
        test_utils.teardown_logger(self)

    def test_load_context(self):
        with configuration.Context(self.good_driver) as context:
            self.assertIsInstance(context, dict)
            self.assertIsInstance(context['strategy'], dict)
            self.assertIsInstance(context['config'], dict)

    @raises(schematics.exceptions.ValidationError)
    def test_check_bad_driver_format(self):
        configuration.Context(self.bad_formatted_driver)

    @raises(InvalidConfiguration)
    def test_validate_bad_config(self):
        bad_config = {}
        ctx = configuration.Context(self.bad_driver)
        ctx._validate(bad_config)

    def test_validate_good_config(self):
        good_config = {
            'universe': 'nasdaq,4',
            'index': pd.date_range('2014/2/3', periods=30, tz=pytz.utc),
            'modules': {
                'algorithm': 'dualma'
            }
        }
        ctx = configuration.Context(self.bad_driver)
        self.assertIsNone(ctx._validate(good_config))

    @raises(InvalidConfiguration)
    def test_validate_bad_index_no_timezone(self):
        good_config = {
            'universe': 'nasdaq,4',
            'index': pd.date_range('2014/2/3', periods=30),
            'modules': {
                'algorithm': 'dualma'
            }
        }
        ctx = configuration.Context(self.bad_driver)
        ctx._validate(good_config)

    @raises(InvalidConfiguration)
    def test_validate_bad_index_empty_dates(self):
        good_config = {
            'universe': 'nasdaq,4',
            'index': pd.date_range('2014/2/3', periods=0),
            'modules': {
                'algorithm': 'dualma'
            }
        }
        ctx = configuration.Context(self.bad_driver)
        ctx._validate(good_config)

    @raises(InvalidConfiguration)
    def test_load_bad_configuration(self):
        ctx = configuration.Context(self.bad_formatted_config)
        ctx.__enter__()

    def test_loaded_configuration(self):
        with configuration.Context(self.good_driver) as context:
            self.assertIn('index', context['config'])
            for field in ['manager', 'algorithm', 'data']:
                self.assertIn(field, context['strategy'])

    @raises(DynamicImportFailed)
    def test_absent_driver_context_load(self):
        ctx = configuration.Context(self.bad_driver)
        ctx.__enter__()
