'''
Tests for intuition.core.configuration
'''

import unittest
import pandas as pd
import intuition.core.configuration as configuration
from dna.errors import ImportContextFailed
from intuition.errors import InvalidConfiguration


class ConfigurationTestCase(unittest.TestCase):

    # FIXME Needs insights installed for these tests
    good_driver = '{}://{}'.format(
        'insights.contexts.file.FileContext',
        'intuition.io/../config/backtest.yml')
    bad_driver = 'no.file.FileContext://intuition.io/../config/backtest.yml'
    bad_config = 'insights.contexts.file.FileContext://intuition.io/fake.yml'
    bad_formatted_config = 'insights.contexts.file.FileContext::/fake.yml'

    def test_logfile(self):
        logfile = configuration.logfile('fake_id')
        self.assertIn('.intuition/logs/fake_id.log', logfile)

    def test_load_context(self):
        with configuration.Context(self.good_driver) as context:
            self.assertIsInstance(context, dict)
            self.assertIsInstance(context['strategy'], dict)
            self.assertIsInstance(context['config'], dict)

    def test_validate_bad_config(self):
        bad_config = {}
        ctx = configuration.Context(self.bad_driver)
        self.assertRaises(
            InvalidConfiguration, ctx._validate, bad_config)

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

    def test_load_bad_configuration(self):
        # TODO Write an invalid file
        pass

    def test_loaded_configuration(self):
        with configuration.Context(self.good_driver) as context:
            for field in ['manager', 'algorithm', 'data']:
                self.assertIn(field, context['strategy'])
            for field in ['index', 'live']:
                self.assertIn(field, context['config'])

    def test_absent_driver_context_load(self):
        ctx = configuration.Context(self.bad_driver)
        self.assertRaises(
            ImportContextFailed, ctx.__enter__)
