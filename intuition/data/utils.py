# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Data related utilities
  ----------------------

  :copyright (c) 2014 Xavier Bruhiere
  :license: Apache 2.0, see LICENSE for more details.
'''

import pandas as pd


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
        assert isinstance(df_to_invert, pd.DataFrame)
        return pd.DataFrame(df_to_invert.to_dict().values(),
                            index=df_to_invert.to_dict().keys())
    return inner


#NOTE with_market symbol, build jxr.pa => JXR:EPA
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
        #NOTE Not very elegant
        data.columns = [s for s in symbols if s.split('.')[0] in data.columns]
        return data
    return decorator
