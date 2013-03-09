#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2012 Xavier Bruhiere
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
import argparse
import time
try:
    sys.path.append(os.environ['QTRADE'])
except:
    # Local config not sourced, does it now
    os.system('source /home/xavier/dev/projects/ppQuanTrade/config.sh')
from neuronquant.utils import setup, log


def clear_log():
    ''' Reset log file with a UNIX trick '''
    log.info('Reseting log file')
    os.system('echo "" > ' + os.environ['QTRADE_LOG'])


def show_process():
    ''' Use system "ps" command to check if server daemons are still running '''
    log.info('Running process:')
    os.system('ps -aux | grep server.js')
    os.system('ps -aux | grep shiny')

def kill_process():
    ''' When done, stop daemons by sending them SIGINT signal '''
    log.info('Killing process...')
    os.system('killall nodejs')
    os.system('killall R')
    # Check
    show_process()

def main(configuration):
    ''' Setup labo: run shiny webapp frontend and node.js distributed bridge
    Parameters
    ----------
    configuration: dict
        local settings, from config.sh
    Returns
    -------
    None
    '''
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
            # Use node.js shiny-server module to ensure public and reliable webapp deployment
            port = '3838'
            app_path = '/users/xavier/shiny-backtest'
            with log.catch_exceptions():
                os.system('sudo ' + '/'.join((root_path, 'network', 'node_modules', '.bin', 'shiny-server')) + ' ' +
                              '/'.join((root_path, 'network', 'shiny-server.config')))
            log.info('{} mode, turned online shiny on {}{}, port {}'.format(configuration['mode'], host, app_path, port))
        else:
            raise ValueError()

        log.info('Opening web-browser to shiny remote interface')
        time.sleep(3)
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
        #NOTE Automatic detection ?
        configuration = {'architecture' : os.environ['QTRADE_CONFIGURATION'],
                         'mode'         : os.environ['QTRADE_MODE']}
        if args.clear:
            clear_log()
        elif args.kill:
            kill_process()
        elif args.ps:
            show_process()
        else:
            main(configuration)
