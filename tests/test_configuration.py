'''
Tests for intuition.core.configuration
'''

import unittest
import intuition.core.configuration as configuration


class ConfigurationTestCase(unittest.TestCase):

    def test_fail_context_load(self):
        conf, strategy = configuration.context('unavailable')
        self.assertTrue('algorithm' in strategy and 'manager' in strategy)
        self.assertFalse(conf)
        self.assertFalse(strategy['algorithm'])
        self.assertFalse(strategy['manager'])
