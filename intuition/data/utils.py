#!/usr/bin/python
# encoding: utf-8
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


from random import shuffle
import os
import pandas as pd


#TODO This is quick and dirty
def detect_exchange(universe):
    if not isinstance(universe, list):
        universe = universe.split(',')
    if universe[0] in Exchanges:
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
        sids_list = FX_PAIRS
    else:
        csv_file = '{}.csv'.format(
            os.path.join(
                os.environ['HOME'], '.intuition/data', exchange.lower()))
        df = pd.read_csv(csv_file)
        sids_list = df['Symbol'].tolist()

    shuffle(sids_list)
    if n > 0:
        sids_list = sids_list[:n]
    return sids_list


def smart_selector(sids):
    if not isinstance(sids, list):
        sids = sids.split(',')
    if sids[0] in Exchanges:
        if len(sids) == 2:
            n = int(sids[1])
        else:
            n = -1
        sids = market_sids_list(sids[0], n)

    return sids


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


FX_PAIRS = ['EUR/USD', 'USD/JPY', 'GBP/USD',
            'EUR/GBP', 'USD/CHF', 'EUR/JPY',
            'EUR/CHF', 'USD/CAD', 'AUD/USD',
            'GBP/JPY', 'AUD/JPY', 'AUD/NZD',
            'CAD/JPY', 'CHF/JPY', 'NZD/USD']


# World exchanges caracteristics
Exchanges = {
    # Market code, from yahoo stock code to google market code (needed for
    # reliable download)
    # Later Londres = LON
    #FIXME Forex is temporary
    'cac40': {'symbol': '^FCHI',
              'timezone': 'Europe/London',
              'code': 1001,
              'google_market': 'EPA'},
    'forex': {'symbol': '^FCHI',
              'timezone': 'Europe/London',
              'indexes': [],
              'code': 1002},
    'nasdaq': {'symbol': '^GSPC',
               'timezone': 'US/Eastern',
               'code': 1003,
               'indexes': ['nasdaq', 'nyse'],
               'google_market': 'NASDAQ'},
    'nyse': {'symbol': '^GSPC',
             'timezone': 'US/Eastern',
             'code': 1004,
             'google_market': 'NYSE'}
}


class Fields:
    QUOTES = ['open', 'low', 'high', 'close', 'volume', 'adj_close']


#TODO Same for google json and xml retrieving
googleCode = dict()


yahooCode = {'ask': 'a', 'average daily volume': 'a2', 'ask size': 'a5',
             'bid': 'b', 'ask rt': 'b2', 'bid rt': 'b3', 'dividend yield': 'y',
             'book value': 'b4', 'bid size': 'b6', 'change and percent': 'c',
             'change': 'c1', 'commission': 'c3', 'change rt': 'c6',
             'after hours change rt': 'c8', 'dividend': 'd',
             'last trade date': 'd1', 'trade date': 'd2', 'earnings': 'e',
             'error': 'e1', 'eps estimate year': 'e7',
             'eps estimate next year': 'e8', 'eps estimate next quarter': 'e9',
             'float shares': 'f6', 'day low': 'g', 'day high': 'h',
             '52-week low': 'j', '52-week high': 'k',
             'holdings gain percent': 'g1', 'annualized gain': 'g3',
             'holdings gain': 'g4', 'holdings gain percent rt': 'g5',
             'holdings gain rt': 'g6', 'more info': 'i', 'order book rt': 'i5',
             'market capitalization': 'j1', 'market cap rt': 'j3',
             'EBITDA': 'j4', 'change from 52-week': 'j5',
             'percent change from 52-week low': 'j6',
             'last trade rt with time': 'k1', 'change percent rt': 'k2',
             'last trade size': 'k3', 'change from 52-week high': 'k4',
             'percent change from 52-week high': 'k5',
             'last trade with time': 'l', 'last trade price': 'l1',
             'high limit': 'l2', 'low limit': 'l3', 'day range': 'm',
             'day range rt': 'm2', '50-day ma': 'm3', '200-day ma': 'm4',
             'percent change from 50-day ma': 'm8', 'name': 'n', 'notes': 'n4',
             'open': 'o', 'previous close': 'p', 'price paid': 'p1',
             'change percent': 'p2', 'price/sales': 'p5', 'price/book': 'p6',
             'ex-dividend date': 'q', 'p/e ratio': 'r', 'dividend date': 'r1',
             'p/e ratio rt': 'r2', 'peg ratio': 'r5',
             'price/eps estimate year': 'r6',
             'price/eps estimate next year': 'r7', 'symbol': 's',
             'shares owned': 's1', 'short ratio': 's7',
             'last trade time': 't1', 'trade links': 't6',
             'ticker trend': 't7', '1 year target price': 't8', 'volume': 'v',
             'holdings value': 'v1', 'holdings value rt': 'v7',
             '52-week range': 'w', 'day value change': 'w1',
             'day value change rt': 'w4', 'stock exchange': 'x'}
