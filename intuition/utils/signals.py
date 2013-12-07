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
import signal
import logbook

log = logbook.Logger('Signal_Manager')


class SignalManager(object):
    def __init__(self, signal_codes=[signal.SIGINT], handlers=[]):
        assert len(signal_codes) >= len(handlers)

        for i in range(len(signal_codes)):
            if i >= len(handlers):
                handlers.append(self.catcher)
            signal.signal(signal_codes[i], handlers[i])

        self.signals = signal_codes
        self.handlers = handlers
        self.alarmed = False

    def catcher(self, signal, frame):
        log.info('Signal code {} catched ({}), calling user method'.format(signal, frame))
        if signal == 2:
            self.shutdown('Shutting down the application...', signal)
        elif signal == 14:
            self.alarmed = True
            log.warning('Alarm timed out...')
        else:
            raise NotImplementedError()

    def shutdown(self, msg, signal=0):
        log.info(msg)
        sys.exit(signal)

    def __repr__(self):
        return '\n'.join(['Signal manager for handling code {}'.format(code) for code in self.signals])

    def __str__(self):
        return self.__repr__()

    def __del__(self):
        log.info('Current signal handler deleted')
