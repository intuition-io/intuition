'''
Tests for intuition.data.universe
'''

import os
import unittest
from nose.tools import eq_
import intuition.data.quandl as quandl


class QuandlDecoratorsTestCase(unittest.TestCase):

    def test__build_nasdaq_quandl_code(self):
        new_symbol = quandl._build_quandl_code('goog')
        eq_(new_symbol, 'GOOG/NASDAQ_GOOG')

    def test__build_cac40_quandl_code(self):
        new_symbol = quandl._build_quandl_code('jxr.pa')
        eq_(new_symbol, 'YAHOO/PA_JXR')

    def test__build_invalid_quandl_code(self):
        new_symbol = quandl._build_quandl_code('e8ver51')
        eq_(new_symbol, 'GOOG/NASDAQ_E8VER51')


# TODO quandl.fetch() tests
class QuandlTestCase(unittest.TestCase):

    def test_initialize_quandl_with_key(self):
        fake_api_key = 'fake'
        qdl = quandl.DataQuandl(fake_api_key)
        eq_(fake_api_key, qdl.quandl_key)

    def test_initialize_quandl_with_environ(self):
        os.environ['QUANDL_API_KEY'] = 'fake'
        qdl = quandl.DataQuandl()
        eq_('fake', qdl.quandl_key)

    def test_initialize_quandl_without_key(self):
        os.environ.pop('QUANDL_API_KEY', None)
        qdl = quandl.DataQuandl()
        self.assertIsNone(qdl.quandl_key)
