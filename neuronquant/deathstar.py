#!/usr/bin/python
# encoding: utf-8
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


from neuronquant.gears.engine import Simulation
from neuronquant.gears.configuration import normalize_date_format
import neuronquant.utils as utils


def trade(mega_config):
    '''
    One function to rule them all
    '''
    from neuronquant.gears.engine import Simulation
    from neuronquant.gears.configuration import normalize_date_format
    import neuronquant.utils as utils
    #from neuronquant.gears.engine import Simulation
    #import neuronquant.utils as utils
    # General simulation behavior
    configuration = mega_config['configuration']
    strategie = mega_config['strategie']

    # Color_setup : Pretty print of errors, warning, and so on
    # Remote_setup: ZMQ based messaging, route logs on the network
    # (catched by server's broker)
    log_setup = (utils.remote_setup if configuration['remote'] else
                 utils.color_setup)
    with log_setup.applicationbound():
        # Backtest or live engine
        engine = Simulation()

        # Setup quotes data and financial context (location, market, ...)
        # simulation from user parameters Wrap _configure_data() and
        # _configure_context() you can use directly for better understanding
        data, trading_context = engine.configure(configuration)

        # See neuronquant/gears/engine.py for details of results which is an
        # analyzes object
        analyzes = engine.run(data, configuration, strategie, trading_context)
        assert analyzes


mega_configuration = {
    'configuration': {
        'cash': 10000,
        'tickers': ['GEMALTO', 'LAFARGE'],
        'port': 5555,
        'exchange': 'paris',
        'db': 'test',
        'algorithm': 'BuyAndHold',
        'frequency': 'daily',
        'manager': 'Constant',
        'start': normalize_date_format('2011-01-10'),
        'end': normalize_date_format('2012-07-03'),
        'remote': False,
        'live': False
    },
    'strategie': {
        'algorithm': {
            'debug': 1,
            'long_window': 200,
            'short_window': 100,
            'threshold': 0
        },
        'manager': {
            'name': 'xavier-remote',
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
