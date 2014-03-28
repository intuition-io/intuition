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

log = dna.logging.logger(__name__)


def _clean_sid(sid):
    sid = str(sid).lower()
    # Remove market extension
    dot_pos = sid.find('.')
    sid = sid[:dot_pos] if dot_pos > 0 else sid
    # Remove forex slash
    return sid.replace('/', '')


def _build_quandl_code(symbol):
    dot_pos = symbol.find('.')
    slash_pos = symbol.find('/')
    if dot_pos > 0:
        market = symbol[dot_pos+1:]
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
    def decorator(self, symbols, **kwargs):
        if not isinstance(symbols, list):
            symbols = [symbols]
        quandl_symbols = map(_build_quandl_code, symbols)
        raw_data = fct(self, quandl_symbols, **kwargs)

        data = {}
        for sid in symbols:
            data[sid] = raw_data.filter(regex='.*{}.*'.format(
                _clean_sid(sid).upper()))
            data[sid].columns = map(
                lambda x: x.replace(' ', '_').lower().split('_-_')[-1],
                data[sid].columns)
        return data
    return decorator


def fractionate_request(fct):
    def inner(self, symbols, **kwargs):
        tolerance_window = 10
        cursor = 0
        data = {}
        while cursor < len(symbols):
            if cursor + tolerance_window > len(symbols):
                limit = len(symbols)
            else:
                limit = cursor + tolerance_window
            symbols_fraction = symbols[cursor:limit]
            cursor += tolerance_window
            data_fraction = fct(self, symbols_fraction, **kwargs)
            for sid, df in data_fraction.iteritems():
                data[sid] = df
        return pd.Panel(data).fillna(method='pad')
    return inner


class DataQuandl(object):
    '''
    Quandl.com as datasource
    '''
    def __init__(self, quandl_key=''):
        self.quandl_key = quandl_key if quandl_key != '' \
            else os.environ["QUANDL_API_KEY"]

    @fractionate_request
    @use_quandl_symbols
    def fetch(self, code, **kwargs):
        '''
        Quandl entry point in datafeed object
        '''
        log.debug('fetching QuanDL data (%s)' % code)
        # This way you can use your credentials even if
        # you didn't provide them to the constructor
        if 'authtoken' in kwargs:
            self.quandl_key = kwargs.pop('authtoken')

        # Harmonization: Quandl call start trim_start
        if 'start' in kwargs:
            kwargs['trim_start'] = kwargs.pop('start')
        if 'end' in kwargs:
            kwargs['trim_end'] = kwargs.pop('end')

        try:
            data = Quandl.get(code, authtoken=self.quandl_key, **kwargs)
            # FIXME With a symbol not found, insert a not_found column
            data.index = data.index.tz_localize(pytz.utc)
            #data.columns = map(
                #lambda x: x.replace(' ', '_').lower(), data.columns)
        except:
            log.error('** unable to fetch %s from Quandl' % code)
            data = pd.DataFrame()
        return data
