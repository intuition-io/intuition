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
import os

from intuition.core.engine import Simulation
from intuition.utils.logger import log, get_nestedlog
import intuition.utils.datautils as datautils
from intuition.core.configuration import Setup


#TODO profiling with http://docs.python.org/2/library/profile.html, http://pycallgraph.slowchop.com/
if __name__ == '__main__':
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
        strategy = setup.get_strategy_configuration(remote=configuration['remote'])

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

        if analyzes is None:
            log.error('** Backtest failed.')
            sys.exit(1)

        '''____________________________________________    Results   ____'''
        #analyzes.run_dashboard(portfolio=strategy['manager']['name'])

        log.info('Portfolio returns: \
                {}'.format(analyzes.results.portfolio_value[-1]))

        if configuration['live'] or analyzes.results.portfolio_value[-1] == configuration['cash']:
            # Currently, live tests don't last more than 20min; analyzes is not
            # relevant, neither backtest without orders
            sys.exit(0)

        #TODO A simple test of recorded vars (zipline feature), works only for Follower algo
        #plot_results(analyzes)

        #NOTE Save only if database id provided, probably temporary solution
        should_save = bool(configuration['database'])

        #TODO Implement in datafeed a generic save method
        # (which could call the correct database save method)
        # Get a portfolio monthly risk analyzis
        perf_series  = analyzes.rolling_performances(timestamp='one_month',
                                                     save=should_save,
                                                     db_id=configuration['database'])

        #TODO save returns not ready yet, don't try to save #TODO Becnhmark was
        # Get daily, cumulative and not, returns of portfolio and benchmark
        returns_df = analyzes.get_returns(
                benchmark=datautils.Exchange[configuration['exchange']]['index'],
                save=False)

        risk_metrics = analyzes.overall_metrics(metrics=perf_series,
                                                save=should_save,
                                                db_id=configuration['database'])

        #FIXME irrelevant results if no transactions were ordered
        log.info('\n\nReturns: {}% / {}%\nVolatility: {} \
                \nSharpe:\t\t{}\nMax drawdown:\t{}\n\n'.format(
                round(risk_metrics['Returns'] * 100.0, 2),
                round(risk_metrics['Benchmark.Returns'] * 100.0, 2),
                round(risk_metrics['Volatility'], 2),
                round(risk_metrics['Sharpe.Ratio'], 2),
                round(risk_metrics['Max.Drawdown'], 2)))

        # If we work in local, draw a quick summary plot
        #FIXME R 3.0.0 apprently broke the script
        sys.exit()
        if not configuration['remote']:
            data = returns_df.drop(['Returns', 'Benchmark.Returns'], axis=1)
            data.plot()
            #plt.show()

            # R statistical analyzes
            #TODO Wrap it in Analyze object using rpy or rest server
            os.system('{}/application/analysis.R --source mysql --table {} --verbose'
                    .format(os.environ['QTRADE'], configuration['database']))
            os.system('evince ./Rplots.pdf')
