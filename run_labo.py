import subprocess
import signal
import os
from logbook import Logger


def main():
    subprocess.call(['clear'])
    log = Logger('Trade Labo')
    log.info('Building up trade laboratory environment...')
    root_path = os.environ['QTRADE']

    log.info('Running remote wrapper for backtest module')
    backtest_worker = subprocess.Popen(['nodejs', '/'.join((root_path, 'network', 'server.js'))], shell=True)
    log.info('Backtester server online (pid:{})'.format(backtest_worker.pid))

    if not backtest_worker.poll():
        backtest_worker.send_signal(signal.SIGINT)  #.kill() or .terminate()

if __name__ == '__main__':
    main()
