# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Intuition remote data
  ---------------------

  Provides functions to access various trading data accross internet wires

  :copyright (c) 2014 Xavier Bruhiere.
  :license: Apache2.0, see LICENSE for more details.
'''

import json
import requests
import pandas as pd
from pandas.io.data import DataReader, get_quote_yahoo
import dna.logging
from intuition.constants import FINANCE_URLS
import intuition.data.ystockquote as ystockquote
import intuition.data.utils as utils

log = dna.logging.logger(__name__)


def historical_pandas_yahoo(symbol, source='yahoo', start=None, end=None):
    '''
    Fetch from yahoo! finance historical quotes
    '''
    # NOTE Panel for multiple symbols ?
    # NOTE Adj Close column name not cool (a space)
    return DataReader(symbol, source, start=start, end=end)


@utils.invert_dataframe_axis
def snapshot_yahoo_pandas(symbols):
    '''
    Get a simple snapshot from yahoo, return dataframe
    __________________________________________________
    Return
        pandas.DataFrame with symbols as index
        and columns = [change_pct, time, last, short_ratio, PE]
    '''
    if isinstance(symbols, str):
        symbols = [symbols]
    # TODO lower() columns
    data = get_quote_yahoo(symbols)
    data.index = [str(sid).lower() for sid in data.index]
    return data


# NOTE Can use symbol with market: 'goog:nasdaq', any difference ?
@utils.fractionate_request
@utils.use_google_symbol
def snapshot_google(symbols):
    payload = {'client': 'ig', 'q': ','.join(symbols)}
    response = requests.get(FINANCE_URLS['snapshot_google_light'],
                            params=payload)
    # FIXME Some errors are not detected
    try:
        json_infos = json.loads(response.text[3:], encoding='utf-8')
    except ValueError:
        log.error("no reliable data found")
        return pd.DataFrame()

    snapshot = {}
    for i, quote in enumerate(json_infos):
        if quote['t'].lower() in map(str.lower, symbols):
            snapshot[symbols[i]] = utils.apply_mapping(
                quote, google_light_mapping)
        else:
            log.warning('Unknown symbol {}, ignoring...'.format(
                quote['t']))

    return pd.DataFrame(snapshot)


@property
def google_light_mapping():
    return {
        'change': (str, 'c'),
        'str_change': (str, 'ccol'),
        'perc_change': (float, 'cp'),
        'exchange': (str, 'e'),
        'id': (int, 'id'),
        'price': (str, 'l'),
        'last_price': (lambda x: x, 'l_cur'),
        'date': (str, 'lt'),
        'time': (str, 'ltt'),
        's': (int, 's'),
        'symbol': (str, 't'),
    }


def lookup_symbol(company):
    ''' Fetch company info
    >>> lookup_symbol("Apple Inc.")
          {u'exch': u'NMS',
           u'market': u'NASDAQ',
           u'name': u'Apple Inc.',
           u'symbol': u'AAPL',
           u'type': u'Equity'}
    '''
    request = requests.get(FINANCE_URLS['info_lookup'].format(company))
    return json.loads(request.text[39:-1])["ResultSet"]["Result"] \
        if request.ok else {'error': request.reason}


def fill_stock_metadata(sid):
    ''' Fetch extra informations about a stock, from yahoo '''
    metadata = {}
    try:
        metadata['name'] = ystockquote.get_company_name(sid)
    except Exception, error:
        log.error(error)
        log.warning('sometimes it just times out, retry later')
        return {}

    metadata['exchange'] = ystockquote.get_stock_exchange(sid)
    if metadata['exchange'].find('Nasdaq') > 0:
        # It returns NasdaqNM
        metadata['exchange'] = 'Nasdaq'
    metadata['type'] = ystockquote.get_type(sid)
    metadata['revenue'] = ystockquote.get_revenue(sid)
    # FIXME Almost never found
    # metadata['index'] = ystockquote.get_indices(sid)
    metadata['sector'] = ystockquote.get_sector(sid)
    metadata['industry'] = ystockquote.get_industry(sid)

    log.debug('successfully fetched metadata about {}'.format(sid))
    log.debug(dna.debug.emphasis(metadata))
    return metadata
