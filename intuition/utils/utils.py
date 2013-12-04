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
        ip = re.compile(r'Address: (\d+\.\d+\.\d+\.\d+)').search(data).group(1)
    else:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('google.com', 0))
        ip = s.getsockname()[0]
    return ip


def BIndexGenerator(start, end, delta=pd.datetools.bday, market=''):
    '''
    @summary generate a business index, avoiding closed market days and hours
    @param start, end, delta: dates informations
    @param market: the concerned market, t guess hours
    @return: a formatted pandas index
    '''
    if delta >= pd.datetools.BDay():
        start += dt.timedelta(hours=23 - start.hour)
    #Business date_range doesn't seem to work
    dates = pd.date_range(start, end, freq=delta)
    #TODO Substracting special days like christmas
    if dates.freq > pd.datetools.Day():
        selector = ((dates.hour > 8) & (dates.hour < 17)) | \
                   ((dates.hour > 16) & (dates.hour < 18) &
                   (dates.minute < 31))
        #return bdays[Markets('euronext').schedule()['selector']]
        return dates[selector]
    return dates


def reIndexDF(df, **kwargs):
    '''
    @summary take a pandas dataframe and reformat
    it according to delta, start and end,
    contrained by closed market days and hours
    '''
    how = kwargs.get('how', np.mean)
    start = kwargs.get('start', df.index[0])
    end = kwargs.get('end', df.index[-1])
    delta_tmp = kwargs.get('delta', df.index[1] - df.index[0])
    market = kwargs.get('market', 'euronext')
    columns = kwargs.get('columns', None)
    if df.index.tzinfo:
        tz = df.index.tzinfo
    else:
        tz = pytz.utc
    assert (not df.empty)
    assert (isinstance(start, dt.datetime) and isinstance(end, dt.datetime))
    assert (isinstance(market, str))
    assert (isinstance(columns, list) or not columns)
    if delta_tmp is None:
        delta_tmp = df.index[1] - df.index[0]
    if isinstance(delta_tmp, dt.timedelta):
        #TODO more offset std or a new way to do it
        if abs(delta_tmp.days - 30) < 5:
            delta = BMonthEnd()
        else:
            delta = pd.DateOffset(days=delta_tmp.days,
                                  minutes=delta_tmp.seconds * 60)
    elif isinstance(delta_tmp, pd.datetools.DateOffset):
        delta = delta_tmp
    else:
        raise ValueError()
    print('[DEBUG] reIndexDF : re-indexing to -> Start: {}, end: {}, delta: {}'
          .format(start, end, delta))
    #if columns:
        #return df.reindex(index = BIndexGenerator(start, end, delta, market), columns=columns).dropna(axis=0)
    #return df.reindex(index=BIndexGenerator(start, end, delta, market))
    if columns:
        df = DataFrame(df.groupby(delta.rollforward).aggregate(how),
                       columns=columns)
    else:
        #FIXME When delta almost the same, error, regular error
        if kwargs.get('reset_hour', False):
            rst_idx = pd.date_range(df.index[0] - pd.datetools.relativedelta(hours=df.index[0].hour),
                df.index[-1] - pd.datetools.relativedelta(hours=df.index[0].hour), freq=delta_tmp)
            df = pd.DataFrame(df, index=rst_idx)
        elif delta.freqstr[-1] == 'M' and abs((df.index[1] - df.index[0]).days - 30) < 5:
            pass
        else:
            df = df.groupby(delta.rollforward).aggregate(how)
    #return df.truncate(before=(start-delta), after=end)
    df = df[(start - delta):end]
    if not df.index.tzinfo:
        df.index = df.index.tz_localize(tz)
    return df


def apply_mapping(raw_row, mapping):
    """
    Override this to hand craft conversion of row.
    """
    row = {target: mapping_func(raw_row[source_key])
           for target, (mapping_func, source_key)
           in mapping.fget().items()}
    return row
