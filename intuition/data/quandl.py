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


""" datafeed.py
Data sources
"""
import pandas as pd
import pytz
import os

import Quandl

import logbook


log = logbook.Logger('intuition.data.quandl')


class DataQuandl(object):
    """
    Quandl as datasource
    """
    def __init__(self, quandl_key=''):
        self.quandl_key = quandl_key if quandl_key != '' \
            else os.environ["QUANDL_API_KEY"]

    #TODO Use of search feature for more powerfull and flexible use
    def fetch(self, code, **kwargs):
        '''
        Quandl entry point in datafeed object
        _____________________________________
        Parameters
            code: str
                quandl data code
            kwargs: dict
                keyword args passed to quandl call
        _____________________________________
        Return:
            data: pandas.dataframe or numpy array
                 returned from quandl call
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
            log.error('** Fetching %s from Quandl' % code)
            data = pd.DataFrame()
        return data
