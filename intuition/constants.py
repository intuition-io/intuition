# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Intuition constants
  -------------------

  :copyright (c) 2014 Xavier Bruhiere
  :license: Apache 2.0, see LICENSE for more details.
'''


import os
from schema import Schema, Optional, Or


DEFAULT_CONFIG = {'algorithm': {}, 'manager': {}}

DEFAULT_LOGPATH = '/tmp'

DEFAULT_HOME = '/'.join([os.environ.get('HOME', '/'), '.intuition'])

# https://github.com/halst/schema
# NOTE Even better ? https://github.com/j2labs/schematics
# TODO More strict validation
CONFIG_SCHEMA = Schema({
    'universe': basestring,
    'index': object,
    # Optional('id'): Use(basestring, error='invalid identity'),
    Optional('id'): basestring,
    #Optional('live'): bool,
    Optional('_id'): object,
    Optional('__v'): object,
    'modules': {
        'algorithm': basestring,
        # TODO It will be at least one
        Optional('backtest'): basestring,
        Optional('live'): basestring,
        Optional('manager'): Or(basestring, None)
    }
})


# Some urls used by the data module to fetch securities infos
FINANCE_URLS = {
    'yahoo_hist': 'http://ichart.yahoo.com/table.csv',
    'yahoo_infos': 'http://finance.yahoo/q/pr',
    'google_prices': 'http://www.google.com/finance/getprices',
    'snapshot_google_light': 'http://www.google.com/finance/info',
    'info_lookup': ('http://d.yimg.com/autoc.finance.yahoo.com/autoc?' +
                    'query={}&callback=YAHOO.Finance.SymbolSuggest.ssCallback')
}
