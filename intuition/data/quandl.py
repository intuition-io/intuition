# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Quandl.com access
  -----------------

  :copyright (c) 2014 Xavier Bruhiere.
  :license: Apache2.0, see LICENSE for more details.
'''


import pandas as pd
import pytz
import os
import dna.logging
import Quandl
import intuition.data.utils as utils

log = dna.logging.logger(__name__)


# http://www.quandl.com/help/api-for-bitcoin-data
BITCOIN_CODE = 'BITCOIN/{market}{currency}'
YAHOO_PARIS_CODE = 'YAHOO/PA_{symbol}'


def _build_quandl_code(symbol):
    dot_pos = symbol.find('.')
    slash_pos = symbol.find('/')
    if dot_pos > 0:
        market = symbol[dot_pos + 1:]
        provider = 'YAHOO'
        symbol = symbol[:dot_pos]
        code = '{}_{}'.format(market, symbol)
    else:
        if slash_pos > 0:
            pair = symbol.split('/')
            provider = 'QUANDL'
            code = '{}{}'.format(pair[0], pair[1])
        else:
            market = 'NASDAQ'
            provider = 'GOOG'
            code = '{}_{}'.format(market, symbol)
    return '{}/{}'.format(provider, code).upper()


def use_quandl_symbols(fct):
    def decorator(symbols, **kwargs):
        if not isinstance(symbols, list):
            symbols = [symbols]
        quandl_symbols = map(_build_quandl_code, symbols)
        raw_data = fct(quandl_symbols, **kwargs)

        data = {}
        for sid in symbols:
            # Filter out other sids
            df_ = raw_data.filter(
                #regex='YAHOO.*_{} -.*'.format(utils.clean_sid(sid).upper())
                regex='.*_{} -.*'.format(utils.clean_sid(sid).upper())
            )
            # Remove Quandl code and useless spaces
            df_.columns = map(
                lambda x: x.replace(' ', '_').lower().split('_-_')[-1],
                df_.columns
            )
            if 'not_found' not in df_.columns:
                data[sid] = df_
            else:
                log.warning('no data was returned for ' + sid)
        return data
    return decorator


@utils.fractionate_request
@use_quandl_symbols
def download(codes, **kwargs):
    try:
        data = Quandl.get(codes, **kwargs)
        data.index = data.index.tz_localize(pytz.utc)
    except Exception, error:
        log.error('unable to fetch {}: {}'.format(codes, error))
        data = pd.DataFrame()

    return data


# NOTE With last simplifications, an object seems useless ?
class DataQuandl(object):
    ''' Quandl.com as datasource '''

    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get('QUANDL_API_KEY', None)

    def fetch(self, codes, **kwargs):
        ''' Quandl entry point in datafeed object '''
        log.debug('fetching QuanDL data (%s)' % codes)

        # Harmonization: Quandl call start trim_start
        if 'start' in kwargs:
            kwargs['trim_start'] = kwargs.pop('start')
        if 'end' in kwargs:
            kwargs['trim_end'] = kwargs.pop('end')

        return download(codes, authtoken=self.api_key, **kwargs)
