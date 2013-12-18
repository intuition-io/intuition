#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2013 xavier
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
import traceback

from intuition.core.engine import Simulation
from intuition.utils.logger import log, get_nestedlog
import intuition.data.utils as datautils
from intuition.core.configuration import Setup


def show_perfs(config, analyzes):
    # Get daily, cumulative and not, returns of portfolio and benchmark
    returns_df = analyzes.get_returns(
        benchmark=datautils.Exchange[config['exchange']]['index'])

    perfs = analyzes.overall_metrics('one_month')

    orders = 0
    for order in analyzes.results.orders:
        orders += len(order)

    final_value = analyzes.results.portfolio_value[-1]
    gain = final_value - config['cash']
    pf_gain_perc = returns_df['CReturns'][-1] * 100.0
    bm_gain_perc = returns_df['Benchmark.CReturns'][-1] * 100.0
    pnl_mean = analyzes.results.pnl.mean()
    pnl_std = analyzes.results.pnl.std()

    print('\n ======================  Results  ==\n')
    log.info('Final value: {} $'.format(final_value))
    log.info('Processed {} orders'.format(orders))
    log.info('Perf: {:.2f}% / {:.2f}%\tGain: {} $'
             .format(pf_gain_perc, bm_gain_perc, gain))
    log.info('Achieved on average a pnl of {} with {} of deviation'
             .format(pnl_mean, pnl_std))
    for k, v in perfs.iteritems():
        log.info('{}: {}'.format(k, v))
    print('\n ===================================\n')


def main():
    '''________________________________________________    Setup    ____
    Setup's goal is to fill 3 dictionnaries :
      - Backtest behavior
      - Strategy parameters (algo(, source) and manager)
      - Environment (global informations like database access)
    '''

    # Dedicated object for configuration setup
    # Searchs and reads ~/.intuition/default.json
    setup = Setup()

    # General simulation behavior is defined using command line arguments
    configuration = setup.parse_commandline()

    # Color_setup : Pretty print of errors, warning, and so on
    # Remote_setup: ZMQ based messaging, route logs on the network
    # (catched by server's broker)
    #TODO Parametric log handler and level
    #log_setup = (utils.remote_setup if configuration['remote'] else
                 #utils.color_setup)

    #FIXME Remote log broken here
    log_setup = get_nestedlog(level=configuration['loglevel'],
                              filename=configuration['logfile'])
    with log_setup.applicationbound():
        '''
        TODO HUGE: Run multiple backtest with communication possibilities (ZMQ)
             for sophisticated multiple strategies strategy
                 - Available capital allocation
                 - Strategies repartition
                 - Use of each-other signals behavior
                 - Global monitoring and evaluation
        '''

        # Fill strategy and manager parameters
        # Localy, reading configuration file
        # Remotely, listening for messages through zmq socket
        strategy = setup.get_strategy_configuration(
            remote=configuration['remote'])

        '''___________________________________________    Backtest    ____'''
        # Backtest or live engine.
        # Registers configuration and setups data client
        engine = Simulation(configuration)

        # Setup quotes data and financial context (location, market, ...)
        # simulation from user parameters. Wraps _configure_data() and
        # _configure_context() you can use directly for better understanding
        data = engine.configure()

        # See intuition/gears/engine.py for details of results
        # which is an Analyzes object
        analyzes = engine.run(data, strategy)

        '''____________________________________________    Results   ____'''
        if analyzes is None:
            log.error('** Backtest failed.')
            sys.exit(1)

        if configuration['live'] or \
                analyzes.results.portfolio_value[-1] == configuration['cash']:
            # Currently, live tests don't last more than 20min; analyzes is not
            # relevant, neither backtest without orders
            sys.exit(0)

        show_perfs(configuration, analyzes)


#TODO profiling with http://docs.python.org/2/library/profile.html,
#                    http://pycallgraph.slowchop.com/
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        log.info('Received SIGINT, cleaning...')
        sys.exit(0)
    except Exception as e:
        log.error("An exception occured : {} ({})".format(e, type(e)))
        print '\n' + 79 * '=' + '\n'
        traceback.print_exc(file=sys.stdout)
        print '\n' + 79 * '=' + '\n'
