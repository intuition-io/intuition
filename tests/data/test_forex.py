'''
Tests for intuition.data.universe
'''

import os
import unittest
from nose.tools import eq_
import intuition.test_utils as test_utils
import intuition.data.forex as forex


class TruefxUtilsTestCase(unittest.TestCase):

    def test__clean_pairs(self):
        cleaned = forex._clean_pairs('usd/gbp')
        eq_(cleaned, 'USD/GBP')
        cleaned = forex._clean_pairs(['usd/gbp', 'USD/JPY'])
        eq_(cleaned, 'USD/GBP,USD/JPY')

    def test__fx_mapping(self):
        pass


# TODO Test api calls
class TruefxTestCase(unittest.TestCase):

    def setUp(self):
        test_utils.setup_logger(self)

    def tearDown(self):
        test_utils.teardown_logger(self)

    def test_initialize_truefx_with_credentials(self):
        fake_credentials = 'login:pass'
        fx = forex.TrueFX(credentials=fake_credentials)
        eq_(fx._user, 'login')
        eq_(fx._pwd, 'pass')
        eq_(fx._full_snapshot, 'y')
        eq_(fx._output_format, 'csv')

    def test_initialize_truefx_with_environ(self):
        os.environ['TRUEFX_API'] = 'login:pass'
        fx = forex.TrueFX()
        eq_(fx._user, 'login')
        eq_(fx._pwd, 'pass')

    def test_initialize_truefx_without_key(self):
        os.environ.pop('TRUEFX_API', None)
        fx = forex.TrueFX()
        eq_(fx._user, '')
        eq_(fx._pwd, '')

    def test_initialize_truefx_with_pairs(self):
        fx = forex.TrueFX(pairs='usd/gbp')
        eq_(fx.state_pairs, 'USD/GBP')
        fx = forex.TrueFX(pairs=['usd/gbp', 'usd/jpy'])
        eq_(fx.state_pairs, 'USD/GBP,USD/JPY')
