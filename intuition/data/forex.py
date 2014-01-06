#
# Copyright 2014 Xavier Bruhiere
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


import requests
import logbook
import os
from pandas import DataFrame, Series


log = logbook.Logger('intuition.data.forex')


def forex_rates(user, password, pairs='', fmt='csv'):
    url = 'http://webrates.truefx.com/rates/connect.html'
    params = '?&q=ozrates&c={}&f={}&s=n'.format(','.join(pairs), fmt)
    auth = requests.get(url + params,
                        auth=(user, password))

    if auth.ok:
        log.debug('[{}] Request successful {}:{}'
                  .format(auth.headers['date'], auth.reason, auth.status_code))
    #return auth.content.split('\n')[:-2]
    return auth.content.split('\n')


def _fx_mapping(raw_response):
    ''' Map raw output to clearer labels '''
    dict_data = dict()
    for pair in raw_response:
        pair = pair.split(',')
        #FIXME Timestamp = year 45173
        dict_data[pair[0]] = {'TimeStamp': pair[1],
                              'Bid.Price': float(pair[2] + pair[3]),
                              'Ask.Price': float(pair[4] + pair[5]),
                              'High': float(pair[6]),
                              'Low': float(pair[7])}
    return dict_data


#FIXME 'Not authorized' mode works weird
class ConnectTrueFX(object):
    auth_url = ('http://webrates.truefx.com/rates/connect.html?\
        u={}&p={}&q=ozrates&c={}&f={}')
    query_url = ('http://webrates.truefx.com/rates/connect.html?\
        id={}&f={}&c={}')

    def __init__(self, credentials='', pairs=[], fmt='csv'):
        #NOTE Without authentification you still can access some data
        #FIXME Not authorized response prevent from downloading quotes.
        #      However later you indeed retrieve 10 defaults
        self._code = None
        if not credentials:
            log.info('No credentials provided, inspecting environment')
            credentials = os.environ.get('TRUEFX_API', ':')

        credentials = credentials.split(':')
        auth = requests.get(
            self.auth_url.format(credentials[0],
                                 credentials[1],
                                 ','.join(pairs), fmt))
        if auth.ok:
            log.debug('[{}] Authentification successful {}:{}'
                      .format(auth.headers['date'],
                              auth.reason,
                              auth.status_code))
            log.debug('Got: {}'.format(auth.content))

        ### Remove '\r\n'
        self._code = auth.content[:-2]

    def query_trueFX(self, pairs='', fmt='csv'):
        ''' Perform a request against truefx data '''
        if isinstance(pairs, str):
            pairs = [pairs]
        response = requests.get(
            self.query_url.format(self._code, fmt, ','.join(pairs)))

        mapped_data = _fx_mapping(response.content.split('\n')[:-2])
        if len(mapped_data) == 1:
            return Series(mapped_data)
        return DataFrame(mapped_data)

    def is_active(self):
        ''' Indicate wether the connection is still on or not '''
        return isinstance(self._code, str) and (self._code != 'not authorized')

    def __del__(self):
        #TODO Deconnection
        pass
