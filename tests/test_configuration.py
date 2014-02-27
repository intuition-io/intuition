'''
Tests for intuition.core.configuration
'''

import unittest
import os
import intuition.core.configuration as configuration
from dna.errors import ImportContextFailed
from intuition.errors import InvalidConfiguration


class ConfigurationTestCase(unittest.TestCase):

    #FIXME File only on my local computer
    good_driver = 'insights.contexts.file::intuition/conf.yaml'
    bad_driver = 'no.where.file::intuition/conf.yaml'
    bad_config = 'insights.contexts.file::/fake.yaml'

    def test_parse_command_line(self):
        try:
            args = None
            args = configuration.parse_commandline()
        except SystemExit:
            self.assertTrue(args is None)
            pass

    def test_load_context(self):
        if os.path.exists(self.good_driver):
            conf, strat = configuration.context(self.good_driver)
            self.assertIsInstance(strat, dict)
            self.assertIsInstance(conf, dict)
        else:
            pass

    def test_load_bad_configuration(self):
        self.assertRaises(
            InvalidConfiguration, configuration.context, self.bad_config)

    def test_loaded_configuration(self):
        if os.path.exists(self.good_driver):
            conf, strat = configuration.context(self.good_driver)
            for field in ['manager', 'algorithm', 'data']:
                self.assertIn(field, strat)
            for field in ['index', 'live', 'exchange']:
                self.assertIn(field, conf)
        else:
            pass

    def test_absent_driver_context_load(self):
        self.assertRaises(
            ImportContextFailed, configuration.context, self.bad_driver)

    def test_logfile(self):
        logfile = configuration.logfile('fake_id')
        self.assertIn('.intuition/logs/fake_id.log', logfile)
