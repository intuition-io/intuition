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
    'exchange': basestring,
    'index': object,
    Optional('_id'): object,
    #Optional('id'): Use(basestring, error='invalid identity'),
    Optional('id'): basestring,
    Optional('live'): bool,
    Optional('frequency'): basestring,
    'modules': {
        'algorithm': basestring,
        'data': basestring,
        Optional('manager'): Or(basestring, None)}})


PANDAS_FREQ = {
    'daily': 'D',
    'hourly': 'H',
    'minutely': 'Min'
}
