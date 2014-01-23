#
# Copyright 2013 Xavier Bruhiere
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


import pandas as pd
import pytz
import os
import logbook

import Quandl


log = logbook.Logger('intuition.data.quandl')


def build_quandl_code(code, market, provider='GOOG'):
    # known providers: YAHOO, GOOG
    return '{}/{}_{}'.format(provider, market, code).upper()


# Ressources : http://www.quandl.com/help/api/resources
# Or the search API : https://github.com/quandl/Python
# Seems to be {PROVIDER}/{MARKET_SUFFIX}_{GOOGLE_SYMBOL}
def use_quandl_symbol(fct):
    def decorator(self, symbol, **kwargs):

        dot_pos = symbol.find('.')
        if dot_pos > 0:
            market = symbol[dot_pos+1:]
            provider = 'YAHOO'
            symbol = symbol[:dot_pos]
        else:
            market = 'NASDAQ'
            provider = 'GOOG'
        quandl_symbol = build_quandl_code(symbol, market, provider)

        return fct(self, quandl_symbol, **kwargs)
    return decorator


def multi_codes(fct):
    '''
    Decorator that allows to use Data.Quandl.fetch with multi codes and get a
    panel of it
    '''
    def build_panel(self, codes, **kwargs):
        if isinstance(codes, str):
            # One code, do nothing special
            data = fct(self, codes, **kwargs)
        elif isinstance(codes, list):
            # Multi codes, build a panel
            tmp_data = {}
            for code in codes:
                tmp_data[code] = fct(self, code, **kwargs)
            data = pd.Panel(tmp_data)
        else:
            raise TypeError('quandl codes must be one string or a list')

        #NOTE The algorithm can't detect missing values this way...
        #NOTE An interpolate() method could be more powerful
        return data.fillna(method='pad')
    return build_panel


class DataQuandl(object):
    '''
    Quandl.com as datasource
    '''
    def __init__(self, quandl_key=''):
        self.quandl_key = quandl_key if quandl_key != '' \
            else os.environ["QUANDL_API_KEY"]

    #TODO Use of search feature for more powerfull and flexible use
    @multi_codes
    @use_quandl_symbol
    def fetch(self, code, **kwargs):
        '''
        Quandl entry point in datafeed object
        '''
        log.debug('fetching QuanDL data (%s)' % code)
        # This way you can use your credentials even if
        # you didn't provide them to the constructor
        if 'authtoken' in kwargs:
            self.quandl_key = kwargs.pop('authtoken')

        # Harmonization: Quandl call start_date trim_start
        if 'start_date' in kwargs:
            kwargs['trim_start'] = kwargs.pop('start_date')
        if 'end_date' in kwargs:
            kwargs['trim_end'] = kwargs.pop('end_date')

        try:
            data = Quandl.get(code, authtoken=self.quandl_key, **kwargs)
            data.index = data.index.tz_localize(pytz.utc)
        except:
            log.error('** unable to fetch %s from Quandl' % code)
            data = pd.DataFrame()
        return data
