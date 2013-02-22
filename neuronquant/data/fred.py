#!/usr/bin/env python
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

