import signal
import sys, os
from LogSubsystem import LogSubsystem

class SignalHandler(object):
    def __init__(self, name='default', err_msg = 'default error', logger=None):
        #TODO: put verbose in kwarg, map it to log level and initialize with it
        if logger == None:
            self._logger = LogSubsystem('SignalHandler', 'debug').getLog()
        else:
            self._logger = logger
        self._name = name
        self._error_msg = err_msg
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGALRM, self.error)

    def shutdown(self, signal, frame):
        self._logger.info('Handler {} received {}, shuting down...'.format(self._name, signal))
        sys.exit(0)

    def error(self, signum, frame):
        self._logger.error('Signal handler {} called with signal {}'.format(self._name, signum))
        raise OSError(self._error_msg)

    def __repr__(self):
        ''' Called when just typed class in the interpreter '''
        return '{} Signal handler'.format(self._name)

    def __str__(self):
        ''' called when class in a print sentence '''
        return self.__repr__()

    def __del__(self):
        self._logger.info('Current signal handler {} deleted'.format(self._name))



''' Usage: Set the signal handler and a 5-second alarm
sh = SignalHandler('Test', 'Error !!!')
signal.alarm(5)

while True:
    continue

signal.alarm(0)          # Disable the alarm
'''
