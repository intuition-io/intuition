#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import time
try:
    sys.path.append(os.environ['QTRADE'])
except:
    os.system('source /home/xavier/dev/projects/ppQuanTrade/config.sh')
from pyTrade.utils import setup, log


def clear_log():
    log.info('Reseting log file')
    os.system('echo "" > ' + os.environ['QTRADE_LOG'])


def show_process():
    log.info('Running process:')
    os.system('ps -aux | grep server.js')
    os.system('ps -aux | grep shiny')

def kill_process():
    log.info('Killing process...')
    os.system('killall nodejs')
    os.system('killall R')
    show_process()

def main(configuration):
    os.system('clear')
    log.info('Building up trade laboratory environment...')
    if configuration['architecture'] == 'local':
        root_path = os.environ['QTRADE']

        log.info('Running remote wrapper for backtest module')
        with log.catch_exceptions():
            os.system('nodejs ' + '/'.join((root_path, 'network', 'server.js' + ' &')))

        log.info('Running remote shiny gui')
        host = 'localhost'
        if configuration['mode'] == 'dev':
            port = '8100'
            app_path = ''
            with log.catch_exceptions():
                os.system('R -q -e "shiny::runApp(\\\"{}/network/shiny-backtest\\\")" &'.format(root_path))
        elif configuration['mode'] == 'prod':
            port = '3838'
            app_path = '/users/xavier/shiny-backtest'
            with log.catch_exceptions():
                os.system('sudo ' + '/'.join((root_path, 'network', 'node_modules', '.bin', 'shiny-server')) + ' ' +
                              '/'.join((root_path, 'network', 'shiny-server.config')))
            log.info('{} mode, turned online shiny on {}{}, port {}'.format(configuration['mode'], host, app_path, port))
        else:
            raise ValueError()

        log.info('Opening web-browser to shiny remote interface')
        time.sleep(2)
        os.system('chromium-browser http://{}:{}{}'.format(host, port, app_path))

    else:
        raise NotImplementedError()
    print('\n\n')
    log.info('Done.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Master script to setup application environnment, both in depth and production mode')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s v0.8.1 Licence rien du tout', help='Print program version')
    parser.add_argument('-c', '--clear', action='store_true', required=False, help='If True, reset application log file')
    parser.add_argument('-p', '--ps', action='store_true', required=False, help='If True, show running nodejs and shiny process')
    parser.add_argument('-k', '--kill', action='store_true', required=False, help='If True, kill nodejs and shiny process')
    args = parser.parse_args()

    with setup.applicationbound():
        #NOTE Future remote backtest implementation, etc...
        #NOTE Automatic detection ?
        configuration = {'architecture': os.environ['QTRADE_CONFIGURATION'],
                         'mode': os.environ['QTRADE_MODE']}
        if args.clear:
            clear_log()
        elif args.kill:
            kill_process()
        elif args.ps:
            show_process()
        else:
            main(configuration)
