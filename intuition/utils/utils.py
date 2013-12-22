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
            pretty_msg = os.linesep.join(
                ["%25s: %s" % (k, obj[k]) for k in sorted(obj.keys())])
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


def apply_mapping(raw_row, mapping):
    """
    Override this to hand craft conversion of row.
    """
    row = {target: mapping_func(raw_row[source_key])
           for target, (mapping_func, source_key)
           in mapping.fget().items()}
    return row


def load_json_file(filename, select_field=None):
    try:
        content = json.load(open(filename, 'r'))
    except:
        print('** loading json configuration.')
        return {}

    # Configuration fields are likely to have several parameter categories
    # If specified, return only 'select_field' one
    return content[select_field] if select_field else content
