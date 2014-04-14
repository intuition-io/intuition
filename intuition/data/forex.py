# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Forex access thanks to truefx.com
  ---------------------------------

  :copyright (c) 2014 Xavier Bruhiere.
  :license: Apache2.0, see LICENSE for more details.
'''


import os
import requests
import string
import random
from pandas import DataFrame, Series
import dna.logging

log = dna.logging.logger(__name__)


def _clean_pairs(pairs):
    if not isinstance(pairs, list):
        pairs = [pairs]
    return ','.join(map(str.upper, pairs))


def _fx_mapping(raw_rates):
    ''' Map raw output to clearer labels '''
    return {pair[0].lower(): {
        'timeStamp': pair[1],
        'bid': float(pair[2] + pair[3]),
        'ask': float(pair[4] + pair[5]),
        'high': float(pair[6]),
        'low': float(pair[7])
    } for pair in map(lambda x: x.split(','), raw_rates)}


class TrueFX(object):

    _api_url = 'http://webrates.truefx.com/rates/connect.html'
    _full_snapshot = 'y'
    _output_format = 'csv'

    def __init__(self, credentials='', pairs=[]):
        if not credentials:
            log.info('No credentials provided, inspecting environment')
            credentials = os.environ.get('TRUEFX_API', ':')

        self._user = credentials.split(':')[0]
        self._pwd = credentials.split(':')[1]
        self.state_pairs = _clean_pairs(pairs)
        #self._qualifier = 'ozrates'
        self._qualifier = ''.join(
            random.choice(string.ascii_lowercase) for _ in range(8))

    def connect(self):
        payload = {
            'u': self._user,
            'p': self._pwd,
            'q': self._qualifier,
            'c': self.state_pairs,
            'f': self._output_format,
            's': self._full_snapshot
        }
        auth = requests.get(self._api_url, params=payload)

        if auth.ok:
            log.debug('Truefx authentification successful')
        # Remove '\r\n'
        self._session = auth.content[:-2]
        return auth.ok

    def query_rates(self, pairs=[]):
        ''' Perform a request against truefx data '''
        # If no pairs, TrueFx will use the ones given the last time
        payload = {'id': self._session}
        if pairs:
            payload['c'] = _clean_pairs(pairs)
        response = requests.get(self._api_url, params=payload)

        mapped_data = _fx_mapping(response.content.split('\n')[:-2])
        return Series(mapped_data) if len(mapped_data) == 1 \
            else DataFrame(mapped_data)
