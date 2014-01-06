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


import sys
import logbook
from logbook.queues import ZeroMQHandler
from logbook.more import ColorizedStderrHandler

from intuition.utils.utils import get_local_ip
import intuition.constants as constants


log = logbook.Logger('intuition.default.logger')


def inject_information(record):
    ''' Add ip information to the logger output '''
    record.extra['ip'] = get_local_ip()


def get_nestedlog(level='debug',
                  show_log=False,
                  filename=constants.DEFAULT_FILE_LOG,
                  uri=None):
    ''' Intuition formated logger '''
    level = level.upper()
    # Default uri: tcp://127.0.0.1:5540
    if uri is not None:
        handlers = [ZeroMQHandler(uri)]
    else:
        handlers = [
            logbook.NullHandler(),
            #logbook.NullHandler(level=logbook.DEBUG, bubble=True),
            #ColorizedStderrHandler(format_string=log_format, level='ERROR'),
            logbook.FileHandler(
                '{}/{}'.format(constants.LOG_DESTINATION, filename),
                level=level)
            #FIXME Doesn't show anything
            #logbook.Processor(inject_information)
        ]
        if show_log:
            handlers.append(
                logbook.StreamHandler(sys.stdout,
                                      format_string=constants.LOG_FORMAT,
                                      level=level))

    return logbook.NestedSetup(handlers)


def get_colorlog():
    return logbook.NestedSetup([
        logbook.StreamHandler(sys.stdout, format_string=constants.LOG_FORMAT),
        ColorizedStderrHandler(format_string=constants.LOG_FORMAT,
                               level='NOTICE'),
        #Processor(inject_information)
    ])
