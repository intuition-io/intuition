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


import os
import json
import re
import socket
from urllib2 import urlopen
#import babel.numbers
#import decimal


def dynamic_import(mod_path, obj_name):
    ''' Take a string and return the corresponding module '''
    try:
        module = __import__(mod_path, fromlist=['whatever'])
    except ImportError, description:
        print(description)
        return None

    if hasattr(module, obj_name):
        obj = getattr(module, obj_name)
    else:
        print('module {} has no attribute {}'.
              format(module.__name__, obj_name))
        return None

    return obj


def activate_pdb_hook():
    ''' Catch exceptions with a prompt for post-mortem analyzis'''
    def debug_exception(type_exception, value, tb):
        import pdb
        pdb.post_mortem(tb)

    import sys
    sys.excepthook = debug_exception


#NOTE Could use pprint module
def emphasis(obj, align=True):
    ''' Clearer data printing '''
    if isinstance(obj, dict):
        if align:
            pretty_msg = os.linesep.join(
                ["%25s: %s" % (k, obj[k]) for k in sorted(obj.keys())])
        else:
            pretty_msg = json.dumps(obj, indent=4, sort_keys=True)
    else:
        return obj
    return pretty_msg


def get_local_ip(public=False):
    ''' Utility for logbook information injection '''
    if public:
        data = str(urlopen('http://checkip.dyndns.com/').read())
        ip_addr = re.compile(
            r'Address: (\d+\.\d+\.\d+\.\d+)').search(data).group(1)
    else:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(('google.com', 0))
        ip_addr = sock.getsockname()[0]
    return ip_addr


def apply_mapping(raw_row, mapping):
    '''
    Override this to hand craft conversion of row.
    '''
    row = {target: mapping_func(raw_row[source_key])
           for target, (mapping_func, source_key)
           in mapping.fget().items()}
    return row
