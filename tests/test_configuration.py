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
    good_driver = 'file::intuition/conf.yaml'
    bad_driver = 'file::intuition/fake.yaml'

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
            self.assertTrue(isinstance(strat, dict))
            self.assertTrue(isinstance(conf, dict))
        else:
            pass

    def test_load_bad_configuration(self):
        try:
            _, __ = configuration.context(self.bad_driver)
        except Exception as error:
            self.assertTrue(type(error) == InvalidConfiguration)

    def test_loaded_configuration(self):
        if os.path.exists(self.good_driver):
            conf, strat = configuration.context(self.good_driver)
            for field in ['manager', 'algorithm', 'data']:
                self.assertTrue(field in strat)
            for field in ['index', 'live', 'exchange']:
                self.assertTrue(field in conf)
        else:
            pass

    def test_absent_driver_context_load(self):
        try:
            _, __ = configuration.context('unavailable')
        except Exception as error:
            self.assertTrue(type(error) == ImportContextFailed)
            self.assertTrue('No module named unavailable' in str(error))
