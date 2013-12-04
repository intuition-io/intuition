#!/usr/bin/python
# encoding: utf-8
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


from neuronquant.gears.configuration import (
    normalize_date_format, smart_tickers_select
)


#from IPython.parallel import require
#from neuronquant.gears.engine import Simulation
#from neuronquant.utils.logger import get_nestedlog
#@require(Simulation, get_nestedlog)
def trade(mega_config):
    '''
    One function to rule them all
    '''
    from neuronquant.gears.engine import Simulation
    from neuronquant.utils.logger import get_nestedlog

    # General simulation behavior
    #NOTE Portfolio server setup in Setup() object,
    #if needed, create it manually here
    configuration = mega_config['configuration']
    strategy = mega_config['strategy']

    # Remote: ZMQ based messaging, route logs on the network
    # (catched by server's broker)
    log_setup = get_nestedlog(level=configuration['loglevel'],
        file=configuration['logfile'])
    with log_setup.applicationbound():
        # Backtest or live engine
        engine = Simulation(configuration)

        # Setup quotes data and financial context (location, market, ...)
        # simulation from user parameters Wrap _configure_data() and
        # _configure_context() you can use directly for better understanding
        data, trading_context = engine.configure()

        # See neuronquant/gears/engine.py for details of results which is an
        # analyzes object
        analyzes = engine.run(data, configuration, strategy, trading_context)
        assert analyzes


def complete_configuration(changes={}, backtest=True):
    # Reset to root_config (doesn't work)
    config = root_configuration.copy()

    #TODO read config['env']  (in setup.configuration)

    if not backtest:
        config['configuration']['live'] = True
        config['configuration']['frequency'] = 'minute'

    for item, value in changes.iteritems():
        if item in config['configuration']:
            config['configuration'][item] = value
        for category in ['algorithm', 'manager']:
            if item in config['strategy'][category]:
                config['strategy'][category][item] = value

    # Check for normalzation
    if isinstance(config['configuration']['start'], unicode) or isinstance(config['configuration']['start'], str):
        config['configuration']['start'] = normalize_date_format(config['configuration']['start'])
    if isinstance(config['configuration']['end'], unicode) or isinstance(config['configuration']['end'], str):
        config['configuration']['end'] = normalize_date_format(config['configuration']['end'])
    if isinstance(config['configuration']['tickers'], unicode) or isinstance(config['configuration']['tickers'], str):
        config['configuration']['tickers'] = smart_tickers_select(config['configuration']['tickers'])
    return config


root_configuration = {
    'configuration': {
        'cash': 50000,
        'loglevel': 'INFO',
        'logfile': 'quantrade.log',
        'tickers': 'random,4',
        'port': 5555,
        'exchange': 'paris',
        'db': 'test',
        'algorithm': 'StdBased',
        'frequency': 'minute',
        'manager': 'Constant',
        'start': '2011-01-10',
        'end': '2012-07-03',
        'remote': False,
        'live': False,
        'source': 'DBPriceSource',
        'env': {}
    },
    'strategy': {
        'algorithm': {
            'debug': 0,
            'long_window': 30,
            'short_window': 25,
            'stddev_window': 9,
            'vwap_window': 5,
            'refresh_period': 1,
            'base_price': 50,
            'save': 1,
            'threshold': 0
        },
        'manager': {
            'name': 'xavier',
            'load_backup': 0,
            'max_weight': 0.3,
            'connected': 0,
            'android': 0,
            'loopback': 60,
            'source': 'mysql',
            'perc_sell': 1.0,
            'buy_amount': 80,
            'sell_amount': 70
        }
    }
}
