# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Data related utilities
  ----------------------

  :copyright (c) 2014 Xavier Bruhiere
  :license: Apache 2.0, see LICENSE for more details.
'''


import os
import intuition.data.data as data
import random
import pandas as pd


def apply_mapping(raw_row, mapping):
    '''
    Override this to hand craft conversion of row.
    '''
    row = {target: mapping_func(raw_row[source_key])
           for target, (mapping_func, source_key)
           in mapping.fget().items()}
    return row


#TODO This is quick and dirty
def detect_exchange(universe):
    if not isinstance(universe, list):
        universe = universe.split(',')
    if universe[0] in data.Exchanges:
        exchange = universe[0]
    else:
        if universe[0].find('/') > 0:
            exchange = 'forex'
        elif universe[0].find('.pa') > 0:
            exchange = 'paris'
        else:
            exchange = 'nasdaq'
    return exchange


def market_sids_list(exchange, n=-1):
    if exchange == 'forex':
        sids_list = data.FX_PAIRS
    else:
        csv_file = '{}.csv'.format(
            os.path.join(
                os.environ['HOME'], '.intuition/data', exchange.lower()))
        df = pd.read_csv(csv_file)
        sids_list = df['Symbol'].tolist()

    random.shuffle(sids_list)
    if n > 0:
        sids_list = sids_list[:n]
    return sids_list


def smart_selector(sids):
    if not isinstance(sids, list):
        sids = sids.split(',')
    if sids[0] in data.Exchanges:
        if len(sids) == 2:
            n = int(sids[1])
        else:
            n = -1
        sids = market_sids_list(sids[0], n)

    #return sids
    return map(str.lower, map(str, sids))


#TODO Complete with :
# http://en.wikipedia.org/wiki/List_of_stock_exchange_opening_times
# http://en.wikipedia.org/wiki/List_of_S&P_500_companies
def filter_market_hours(dates, exchange):
    ''' Only return market open hours from UTC timezone'''
    #NOTE UTC times ! Beware of summer and winter hours
    if dates.freq >= pd.datetools.Day():
        # Daily or lower frequency, no hours filter required
        return dates
    if exchange == 'paris':
        selector = ((dates.hour > 6) & (dates.hour < 16)) | \
            ((dates.hour == 17) & (dates.minute < 31))
    elif exchange == 'london':
        selector = ((dates.hour > 8) & (dates.hour < 16)) | \
            ((dates.hour == 16) & (dates.minute > 31))
    elif exchange == 'tokyo':
        selector = ((dates.hour > 0) & (dates.hour < 6))
    elif exchange == 'nasdaq' or exchange == 'nyse':
        selector = ((dates.hour > 13) & (dates.hour < 21)) | \
            ((dates.hour == 13) & (dates.minute > 31))
    else:
        # Forex or Unknown market, return as is
        return dates

    # Pandas dataframe filtering mechanism
    return dates[selector]


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
