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

import logbook
from logbook.queues import ZeroMQHandler
from logbook.more import ColorizedStderrHandler

from utils import get_local_ip


log = logbook.Logger('intuition.default.logger')

log_format = u'{record.extra["ip"]} [{record.time:%m-%d %H:%M}] {record.level_name}::{record.channel} - {record.message}'

default_log_destination = os.path.expanduser('~/.intuition/logs')
log_destination = default_log_destination \
    if os.path.exists(default_log_destination) else '/tmp'
default_file_log = 'intuition.log'


def inject_information(record):
    record.extra['ip'] = get_local_ip()


def get_nestedlog(level='debug', show_log=False, filename=default_file_log, uri=None):
    level = level.upper()
    # Default uri: tcp://127.0.0.1:5540
    if uri is not None:
        handlers = [ZeroMQHandler(uri)]
    else:
        handlers = [
            logbook.NullHandler(),
            #logbook.NullHandler(level=logbook.DEBUG, bubble=True),
            #ColorizedStderrHandler(format_string=log_format, level='ERROR'),
            logbook.FileHandler('{}/{}'.format(log_destination, filename), level=level)
            #FIXME Doesn't show anything
            #logbook.Processor(inject_information)
        ]
        if show_log:
            handlers.append(
                logbook.StreamHandler(sys.stdout,
                                      format_string=log_format,
                                      level=level))

    return logbook.NestedSetup(handlers)


color_setup = logbook.NestedSetup([
    logbook.StreamHandler(sys.stdout, format_string=log_format),
    ColorizedStderrHandler(format_string=log_format, level='NOTICE'),
    #Processor(inject_information)
])

#remote_setup = logbook.NestedSetup([
    #ZeroMQHandler('tcp://127.0.0.1:56540'),
    ##Processor(inject_information)
#])
