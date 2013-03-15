#!/usr/bin/env python
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


""" fred.py

Python interface to the St.Louis Fed's Federal Reserve Economic Data
"""

import urllib
from xml.etree import ElementTree
from datetime import date
from time import mktime, strptime

indicators = {'bank_prime_loan_rate': 'DPRIME',
              'consumer_price_index': 'SOMETHING'}


FRED_API_KEY = '34a7386da77efa763957d30a167376aa'


def _get_url(fname):
    return 'http://api.stlouisfed.org/fred/series/observations?series_id=' + fname + '&api_key=' + FRED_API_KEY

def _get_raw(fname):
    tree = ElementTree.fromstring(urllib.urlopen(_get_url(fname)).read())
    observations = tree.iter('observation')
    return {'dates': [date.fromtimestamp(mktime(strptime(obs.get('date'), '%Y-%m-%d'))) for obs in tree.iter('observation')],
            'values': [float(obs.get('value')) for obs in tree.iter('observation')]}

def get(indicator):
    return _get_raw(indicators[indicator])

