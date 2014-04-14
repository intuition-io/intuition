# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  data informations
  -----------------

  :copyright (c) 2014 Xavier Bruhiere.
  :license: Apache2.0, see LICENSE for more details.
'''


"""
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
    'forex': {'symbol': '^GSPC',
              'timezone': 'US/Eastern',
              'code': 1002,
              'indexes': []},
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
"""


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
