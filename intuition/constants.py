# -*- coding: utf-8 -*-
# vim:fenc=utf-8


import os
from schema import Schema, Optional, Or


DEFAULT_CONFIG = {'algorithm': {}, 'manager': {}}
MODULES_PATH = os.environ.get('MODULES_PATH', 'insights')

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
    'modules': {
        'algorithm': basestring,
        'data': basestring,
        Optional('manager'): Or(basestring, None)}})
