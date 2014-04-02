# -*- coding: utf-8 -*-
# vim:fenc=utf-8


import os
from schema import Schema, Optional, Or


DEFAULT_CONFIG = {'algorithm': {}, 'manager': {}}

DEFAULT_LOGPATH = '/tmp'

DEFAULT_HOME = '/'.join([os.environ.get('HOME', '/'), '.intuition'])

# https://github.com/halst/schema
#NOTE Even better ? https://github.com/j2labs/schematics
#TODO More strict validation
CONFIG_SCHEMA = Schema({
    'universe': basestring,
    'index': object,
    Optional('_id'): object,
    #Optional('id'): Use(basestring, error='invalid identity'),
    Optional('id'): basestring,
    Optional('live'): bool,
    Optional('frequency'): basestring,
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


PANDAS_FREQ = {
    'daily': 'D',
    'hourly': 'H',
    'minutely': 'Min'
}
