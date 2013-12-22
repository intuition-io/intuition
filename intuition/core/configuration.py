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


import argparse
import logbook
import os
import sys
import pytz
import datetime

import intuition.utils.utils as utils
import intuition.data.utils as datautils
import intuition.utils.dates as datesutils


log = logbook.Logger('intuition.core.configuration')


class Setup():
    ''' Configuration object for the Trading engine'''
    config_backtest = {}
    config_strategy = {}

    def __init__(self, config_dir=''):
        '''
        Parameters
            configuration_folder: str
                default is current location for configuration files
        '''
        #NOTE timezone as parameter ?
        #FIXME This is not reflected on database.py and portfolio.py, neither
        #      logger.py
        default_config_dir = '/'.join([os.environ['HOME'], '.intuition'])
        self.configuration_folder = config_dir if config_dir \
            else default_config_dir

        self.strategy_file = '/'.join([
            self.configuration_folder, 'plugins.json'])

    def parse_commandline(self):
        '''
        Read command lines arguments and map them
        to a more usuable dictionnary
        _________________________________________
        Return
            self.config_backtest: dict():
                Backtest simulator parameters
        '''
        log.debug('Reading commandline arguments')

        parser = argparse.ArgumentParser(
            description='Intuition, the terrific trading system')
        parser.add_argument('-v', '--version',
                            action='version',
                            version='%(prog)s v0.1.3 Licence Apache 2.0',
                            help='Print program version')
        parser.add_argument('-sl', '--showlog',
                            action='store_true',
                            help='Print logs on stdout')
        parser.add_argument('-f', '--frequency',
                            type=str, action='store', default='daily',
                            required=False,
                            help='(pandas) events frequency')
        parser.add_argument('-a', '--algorithm',
                            action='store',
                            required=True, help='Trading algorithm to be used')
        parser.add_argument('-m', '--manager',
                            action='store', default='',
                            required=False,
                            help='Portfolio strategy to be used')
        parser.add_argument('-so', '--source',
                            action='store',
                            required=True, help='Data generator')
        parser.add_argument('-u', '--universe',
                            action='store', default='cac40,5',
                            required=False, help='target names to process')
        parser.add_argument('-s', '--start',
                            action='store', default='',
                            required=False, help='Start date of the engine')
        parser.add_argument('-e', '--end',
                            action='store',
                            default='',
                            required=False, help='Stop date of the backtester')
        args = parser.parse_args()

        exchange = datautils.detect_exchange(args.universe)

        dummy_dates = datesutils.build_date_index(args.start, args.end)
        #TODO Use zipline style to filter instead
        trading_dates = datautils.filter_market_hours(dummy_dates, exchange)
        if len(trading_dates) == 0:
            log.warning('! Market closed.')
            sys.exit(0)

        is_live = (datetime.datetime.now(tz=pytz.utc) < trading_dates[-1])

        log.debug('Mapping arguments to backtest parameters dictionnary')
        self.config_backtest = {'algorithm': args.algorithm,
                                'manager': args.manager,
                                'source': args.source,
                                'universe': args.universe.split(','),
                                'exchange': exchange,
                                'index': trading_dates,
                                'live': is_live,
                                'showlog': args.showlog}

        return self.config_backtest

    def get_strategy_configuration(self, *args, **kwargs):
        '''
        Read localy strategy's parameters
        '''
        # If no command line was parsed you can use manually a dict
        # for config_backtest or must specify it outside
        if 'config_backtest' in kwargs:
            self.config_backtest = kwargs.pop('config_backtest')
        else:
            assert self.config_backtest

        log.info('Reading strategy configuration from json files')
        for field in ['manager', 'algorithm']:
            self.config_strategy[field] = utils.load_json_file(
                self.strategy_file,
                select_field=field)

        log.info('Strategy configuration is Done.')

        return self.config_strategy
