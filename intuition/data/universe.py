# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Universe manager
  ----------------

  It knows everything about market and smartly handle user input

  :copyright (c) 2014 Xavier Bruhiere
  :license: Apache 2.0, see LICENSE for more details.
'''


import os
import random
import yaml
import dna.logging
from intuition.errors import LoadMarketSchemeFailed

log = dna.logging.logger(__name__)


class Market(object):
    '''
    Knows everything about market and smartly handle user input
    '''

    # TODO Read default from market.yml or set by the user
    benchmark = '^GSPC'
    timezone = 'US/Eastern'
    raw_description = None
    scheme_path = os.path.expanduser('~/.intuition/data/market.yml')

    def __init__(self):
        log.info('loading market scheme')
        self._load_market_scheme()

    def _load_market_scheme(self):
        ''' Load market yaml description '''
        try:
            self.scheme = yaml.load(open(self.scheme_path, 'r'))
        except Exception, error:
            raise LoadMarketSchemeFailed(reason=error)

    def _extract_forex(self):
        self.timezone = self.scheme['forex']['timezone']
        return self.scheme['forex']['pairs']

    def _extract_cac40(self, market):
        market_scheme = self.scheme
        # Walk the market structure
        for key in market[:-1]:
            market_scheme = market_scheme[key]

        self.timezone = market_scheme['timezone']
        self.benchmark = market_scheme['benchmark']
        return map(
            lambda x: x + '.pa',
            market_scheme[market[-1]].keys())

    def _lookup_sids(self, market, limit=-1):
        market = market.split(':')

        try:
            if 'forex' in market:
                sids = self._extract_forex()
            elif 'paris' in market:
                sids = self._extract_cac40(market)
            else:
                raise NotImplementedError(
                    'market {} not supported'.format(market))
        except Exception, error:
            raise LoadMarketSchemeFailed(reason=error)

        random.shuffle(sids)
        return sids[:limit] if limit > 0 else sids

    # TODO multi exchange, sector and other criterias
    def parse_universe_description(self, description):
        ''' Semantic

           - 'sid1,sid2,sid2,...'
           - 'exchange' : every sids of the exchange
           - 'exchange,n' : n random sids of the exchange

        where exchange is a combination of 'type:index:submarket'
        '''
        self.raw_description = description
        description = description.split(',')
        self.exchange = description[0]

        n = int(description[1]) if len(description) == 2 else -1
        self.sids = self._lookup_sids(description[0], n)

    def _detect_exchange(self, description):
        ''' Guess from the description and the market scheme '''
        pass

    def filter_open_hours(self, index):
        ''' Remove market specific closed hours '''
        return index

    def __str__(self):
        return '<sids: {} exchange: {} timezone: {} benchmark: {}'.format(
            self.sids, self.exchange, self.timezone, self.benchmark)


#TODO Complete with :
# http://en.wikipedia.org/wiki/List_of_stock_exchange_opening_times
# http://en.wikipedia.org/wiki/List_of_S&P_500_companies
"""
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
    index = dates[selector]
    if not index.size:
        raise ExchangeIsClosed(exchange=exchange, dates=dates)
    return index
"""
