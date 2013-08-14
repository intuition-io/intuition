#
# Copyright 2012 Xavier Bruhiere
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


import datetime as dt
import pytz

import pandas as pd
from pandas import DataFrame
from pandas.core.datetools import BMonthEnd
import numpy as np
import json
import os

#import babel.numbers
#import decimal

import re
import socket
from urllib2 import urlopen


def activate_pdb_hook():
    def debug_exception(type, value, tb):
        import pdb
        pdb.post_mortem(tb)

    import sys
    sys.excepthook = debug_exception


#NOTE Could use pprint module
def emphasis(obj, align=True):
    if isinstance(obj, dict):
        if align:
            pretty_msg = os.linesep.join(["%25s: %s" % (k, obj[k]) for k in sorted(obj.keys())])
        else:
            pretty_msg = json.dumps(obj, indent=4, sort_keys=True)
    else:
        return obj
    return pretty_msg


def to_dict(obj):
    try:
        dict_obj = obj.__dict__
    except:
        print '** Error: Cannot casting to dictionnary'
        return obj
    for key, value in dict_obj.iteritems():
        if key.find('date') >= 0:
            dict_obj[key] = value.strftime(format='%Y-%m-%d %H:%M')
    return dict_obj


def get_local_ip(public=False):
    if public:
        data = str(urlopen('http://checkip.dyndns.com/').read())
        return re.compile(r'Address: (\d+\.\d+\.\d+\.\d+)').search(data).group(1)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('google.com', 0))
    return s.getsockname()[0]


def apply_mapping(raw_row, mapping):
    """
    Override this to hand craft conversion of row.
    """
    row = {target: mapping_func(raw_row[source_key])
           for target, (mapping_func, source_key)
           in mapping.fget().items()}
    return row


def complete_configuration(root_configuration, changes={}):
    # Reset to root_config (doesn't work)
    config = root_configuration.copy()

    #TODO read config['env']  (in setup.configuration)

    for item, value in changes.iteritems():
        if item in config['configuration']:
            config['configuration'][item] = value
        for category in ['algorithm', 'manager']:
            if item in config['strategie'][category]:
                config['strategie'][category][item] = value

    # Check for normalzation
    #TODO Generic date detection, etc...
    if isinstance(config['configuration']['start'], unicode) or isinstance(config['configuration']['start'], str):
        config['configuration']['start'] = normalize_date_format(config['configuration']['start'])
    if isinstance(config['configuration']['end'], unicode) or isinstance(config['configuration']['end'], str):
        config['configuration']['end'] = normalize_date_format(config['configuration']['end'])
    if isinstance(config['configuration']['tickers'], unicode) or isinstance(config['configuration']['tickers'], str):
        config['configuration']['tickers'] = smart_tickers_select(config['configuration']['tickers'])
    return config
