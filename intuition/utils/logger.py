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
import sys

#NOTE Database:
# http://pythonhosted.org/Logbook/api/ticketing.html#module-logbook.ticketing
import logbook
from logbook.queues import ZeroMQHandler
from logbook.more import ColorizedStderrHandler

from utils import get_local_ip

log_format = u'{record.extra["ip"]} [{record.time:%m-%d %H:%M}] {record.channel}::{record.level_name} - {record.message}'

default_log_destination = os.path.expanduser('~/.intuition/logs')
log_destination = default_log_destination if os.path.exists(default_log_destination) else '/tmp'


def inject_information(record):
    record.extra['ip'] = get_local_ip()


def get_nestedlog(level='DEBUG', filename='intuition.log', uri=None):
    # Default uri: tcp://127.0.0.1:5540
    if uri is not None:
        log_setup = logbook.NestedSetup([
            ZeroMQHandler(uri),
        ])
    else:
        log_setup = logbook.NestedSetup([
            logbook.NullHandler(),
            #logbook.NullHandler(level=logbook.DEBUG, bubble=True),
            ColorizedStderrHandler(format_string=log_format, level='ERROR'),
            logbook.StreamHandler(sys.stdout, format_string=log_format),
            logbook.FileHandler('{}/{}'.format(log_destination, filename), level=level)
            #FIXME Doesn't show anything
            #logbook.Processor(inject_information)
        ])

    return log_setup


# a nested handler setup can be used to configure more complex setups
setup = logbook.NestedSetup([
    #logbook.StderrHandler(format_string=u'[{record.time:%Y-%m-%d %H:%M}] {record.channel} - {record.level_name}: {record.message} \t({record.extra[ip]})'),
    logbook.StreamHandler(sys.stdout, format_string=log_format),
    # then write messages that are at least warnings to to a logfile
    #FIXME FileHandler(os.environ['QTRADE_LOG'], level='WARNING'),
    logbook.FileHandler('{}/{}'.format(log_destination, 'quantrade.log'), level='WARNING'),
    #Processor(inject_information)
])

color_setup = logbook.NestedSetup([
    logbook.StreamHandler(sys.stdout, format_string=log_format),
    ColorizedStderrHandler(format_string=log_format, level='NOTICE'),
    #Processor(inject_information)
])

#remote_setup = logbook.NestedSetup([
    #ZeroMQHandler('tcp://127.0.0.1:56540'),
    ##Processor(inject_information)
#])

log = logbook.Logger('intuition.default.logger')
