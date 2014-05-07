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
import pytz
import yaml
import datetime as dt
import pandas as pd
import dateutil.parser
import dna.logging
from intuition.errors import LoadMarketSchemeFailed

log = dna.logging.logger(__name__)


# TODO Move it to utils
def timezone_aware_parser(date, timezone='UTC'):
    return pytz.timezone(timezone)\
        .localize(dateutil.parser.parse(date))\
        .astimezone(pytz.utc)


class Tick(object):
    '''
    Represent a convenient clock, utc aware, through 3 attributes:
      - start : datetime low limit [default is midnight]
      - delta : timestamp between ticks [default is 1h]
      - end   : datetime high limit [default is next midnight]
    '''

    def __init__(self, **kwargs):
        _default_start = pd.datetools.normalize_date(
            dt.datetime.now(tz=pytz.utc))
        _default_end = pd.datetools.normalize_date(
            dt.datetime.now(tz=pytz.utc) + dt.timedelta(days=1))
        _default_delta = dt.timedelta(hours=1)

        self.start = kwargs.get('start', _default_start)
        self.end = kwargs.get('end', _default_end)
        self.delta = kwargs.get('delta', _default_delta)
        self._tz = kwargs.get('tz', 'UTC')

    @property
    def tack(self):
        current_date = self.start
        while current_date < self.end:
            yield current_date
            current_date += self.delta

    def _parse_punctual(self, human_time):
        '''
        Translate human-like approximations to datetime
          - "at opening" => self.start + 5 minutes
          - "at midday" => self.end + self.start / 2
          - "at opening" => self.start + 5 minutes
          - "at X o'clock" => parse(Xh00)
          - "at xxhxx" => parse(xxhxx)
        '''
        tokens = human_time.split()
        self.delta = dt.timedelta(days=1)

        if human_time.find('opening') > 0:
            self.start = self.start + dt.timedelta(minutes=5)

        elif human_time.find('midday') > 0:
            self.start += (self.end - self.start) / 2

        elif human_time.find('closing') > 0:
            self.start = self.end - dt.timedelta(minutes=5)

        elif human_time.find('clock') > 0:
            today_start = timezone_aware_parser(tokens[1] + 'h00', self._tz)
            self.start = self.start.replace(
                hour=today_start.hour, minute=today_start.minute)

        elif human_time.find('h') > 0:
            today_start = timezone_aware_parser(tokens[1], self._tz)
            self.start = self.start.replace(
                hour=today_start.hour, minute=today_start.minute)

        else:
            raise ValueError('unable to parse ' + human_time)

    def _parse_constant_frequency(self, human_time):
        ''' Parse an input like "every 30 {hours,minutes}" '''
        tokens = human_time.split()

        if tokens[-1].lower() == 'minutes':
            self.delta = dt.timedelta(minutes=float(tokens[1]))

        elif tokens[-1].lower() == 'hours':
            self.delta = dt.timedelta(hours=float(tokens[1]))

        else:
            raise ValueError('unable to parse ' + human_time)

    def parse(self, human_time):
        ''' Set self.start and self.delta from a human timestamp input '''
        if human_time.find('every') >= 0:
            self._parse_constant_frequency(human_time)

        elif human_time.find('at') >= 0:
            self._parse_punctual(human_time)

        else:
            raise ValueError('unable to parse ' + human_time)


class Market(object):
    '''
    Knows everything about market and smartly handle user input
    '''

    # TODO Read default from market.yml or set by the user
    benchmark = '^GSPC'
    default_timezone = 'US/Eastern'
    default_open = '00h01'
    default_close = '23h59'
    exchange = None
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
        self.scheme = self.scheme['currencies']['forex']
        return self.scheme['pairs']

    def _extract_cac40(self, market):
        market_scheme = self.scheme
        # Walk the market structure
        for key in market[:-1]:
            market_scheme = market_scheme[key]

        self.scheme = market_scheme
        self.benchmark = market_scheme['benchmark']
        return map(
            lambda x: x + '.pa',
            market_scheme[market[-1]].keys())

    @property
    def timezone(self):
        return self.scheme.get('timezone') or self.default_timezone

    @property
    def open(self):
        safe_open = self.scheme.get('open') or self.default_open
        return timezone_aware_parser(safe_open, self.timezone)

    @property
    def close(self):
        # Check if a specific market scheme was set
        safe_close = self.scheme.get('close') or self.default_close
        return timezone_aware_parser(safe_close, self.timezone)

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

    def __str__(self):
        return '<sids: {} exchange: {} timezone: {} benchmark: {}'.format(
            self.sids, self.exchange, self.timezone, self.benchmark)
