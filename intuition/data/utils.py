# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Data related utilities
  ----------------------

  :copyright (c) 2014 Xavier Bruhiere
  :license: Apache 2.0, see LICENSE for more details.
'''

import pandas as pd


# TODO Make it a decorator
def clean_sid(sid):
    sid = str(sid).lower()
    # Remove market extension
    dot_pos = sid.find('.')
    sid = sid[:dot_pos] if dot_pos > 0 else sid
    # Remove forex slash
    return sid.replace('/', '')


def apply_mapping(raw_row, mapping):
    '''
    Override this to hand craft conversion of row.
    '''
    row = {target: mapping_func(raw_row[source_key])
           for target, (mapping_func, source_key)
           in mapping.fget().items()}
    return row


def invert_dataframe_axis(fct):
    '''
    Make dataframe index column names,
    and vice et versa
    '''
    def inner(*args, **kwargs):
        df_to_invert = fct(*args, **kwargs)
        return pd.DataFrame(df_to_invert.to_dict().values(),
                            index=df_to_invert.to_dict().keys())
    return inner


# NOTE with_market symbol, build jxr.pa => JXR:EPA
def use_google_symbol(fct):
    '''
    Removes ".PA" or other market indicator from yahoo symbol
    convention to suit google convention
    '''
    def decorator(symbols):
        google_symbols = []

        # If one symbol string
        if isinstance(symbols, str):
            symbols = [symbols]

        symbols = sorted(symbols)
        for symbol in symbols:
            dot_pos = symbol.find('.')
            google_symbols.append(
                symbol[:dot_pos] if (dot_pos > 0) else symbol)

        data = fct(google_symbols)
        # NOTE Not very elegant
        data.columns = [s for s in symbols if s.split('.')[0] in data.columns]
        return data
    return decorator


def fractionate_request(fct):
    def inner(symbols, **kwargs):
        tolerance_window = 10
        cursor = 0
        data = {}
        df = pd.DataFrame()
        while cursor < len(symbols):
            if cursor + tolerance_window > len(symbols):
                limit = len(symbols)
            else:
                limit = cursor + tolerance_window
            symbols_fraction = symbols[cursor:limit]
            cursor += tolerance_window
            data_fraction = fct(symbols_fraction, **kwargs)
            for sid, df in data_fraction.iteritems():
                if not df.empty:
                    data[sid] = df

        if isinstance(df, pd.Series):
            data = pd.DataFrame(data)
        elif isinstance(df, pd.DataFrame):
            data = pd.Panel(data)
        else:
            raise NotImplementedError(type(df))
        return data.fillna(method='pad')
    return inner
