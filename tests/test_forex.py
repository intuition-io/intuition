#
# Copyright 2012 Xavier Bruhiere
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


'''
Tests for the forex datasource
'''

from unittest import TestCase
from nose.tools import timed

from neuronquant.data.forex import ConnectTrueFX
#from neuronquant.utils.datautils import FX_PAIRS

DEFAULT_TIMEOUT = 15
EXTENDED_TIMEOUT = 90


class TestForex(TestCase):
    '''
    Forex access through TrueFX provider
    !! Beware that truefx server will return empty array
    if currencies were not updated since last call
    '''
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_connection_credentials(self):
        '''
        Use explicit TrueFx username and password account for
        authentification
        '''
        client = ConnectTrueFX(user='Gusabi', password='quantrade')
        # If succeeded, an authentification for further use was returned by
        # truefx server
        assert client
        assert client._code
        assert client._code.find('Gusabi') == 0

    def test_connection_default_auth_file(self):
        '''
        If no credentials, the constructor tries to find it
        reading config/default.json
        '''
        # It's default behavior, nothing to specifie
        client = ConnectTrueFX()
        assert client
        assert client._code
        assert client._code.find('Gusabi') == 0

    def test_connection_custom_auth_file(self):
        '''
        If no credentials, the constructor tries to find it
        reading given json file
        '''
        client = ConnectTrueFX(auth_file='plugins.json')
        assert client
        assert client._code
        assert client._code.find('Gusabi') == 0

    def test_connection_without_auth(self):
        ''' TrueFX API can be used without credentials in a limited mode '''
        #FIXME Fails to retrieve limited values
        client = ConnectTrueFX(user=None, password=None, auth_file='fake.json')
        assert client._code == 'not authorized'

    def test_connection_with_pairs(self):
        pairs = ['EUR/USD', 'USD/JPY']
        client = ConnectTrueFX(pairs=pairs)
        ### Default call use pairs given during connection
        dataframe = client.QueryTrueFX()
        for p in pairs:
            assert p in dataframe.columns

    @timed(DEFAULT_TIMEOUT)
    def test_query_default(self):
        pass

    def test_query_format(self):
        pass

    def test_query_pairs(self):
        pass

    def test_response_formating(self):
        pass

    def test_detect_active(self):
        pass

    def test_standalone_request(self):
        pass
