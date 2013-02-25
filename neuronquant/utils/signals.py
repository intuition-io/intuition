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


''' Usage: Set the signal handler and a 5-second alarm
sh = SignalHandler('Test', 'Error !!!')
signal.alarm(5)
while True:
    continue
signal.alarm(0)          # Disable the alarm
'''
