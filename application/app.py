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

import sys
import os

import pylab as plt

from neuronquant.gears.engine import Simulation
import neuronquant.utils as utils
import neuronquant.utils.datautils as datautils
from neuronquant.gears.configuration import Setup


if __name__ == '__main__':
    '''___________________________________________________________________________________________    Setup    ____'''
    # Dedicated object for configuration setup
    setup = Setup()

    # General simulation behavior is defined using command line arguments
    configuration = setup.parse_commandline()

    # Color_setup : Pretty print of errors, warning, and so on
    # Remote_setup: ZMQ based messaging, route logs on the network
    # (catched by server's broker)
    log_setup = (utils.remote_setup if configuration['remote'] else
                 utils.color_setup)
    with log_setup.applicationbound():

        # Fill strategie and manager parameters
        # Localy, reading configuration file
        # Remotely, listening gor messages through zmq socket
        strategie = setup.get_strategie_configuration(remote=configuration['remote'])

        '''____________________________________________________________________________________    Backtest    ____'''
        # Backtest or live engine
        engine = Simulation()

        # Setup quotes data and financial context (location, market, ...)
        # simulation from user parameters Wrap _configure_data() and
        # _configure_context() you can use directly for better understanding
        data, trading_context = engine.configure(configuration)

        # See neuronquant/calculus/engine.py for details of results which is an
        # analyzes object
        analyzes = engine.run(data, configuration, strategie, trading_context)

        if analyzes is None:
            utils.log.error('** Backtest failed.')
            sys.exit(1)

        '''_______________________________________________________________________________________    Results   ____'''
        utils.log.info('Portfolio returns: \
                {}'.format(analyzes.results.portfolio_value[-1]))

        if configuration['live'] or analyzes.results.portfolio_value[-1] == configuration['cash']:
            # Currently, live tests don't last more than 20min; analyzes is not
            # relevant, neither backtest without orders
            sys.exit(0)

        #TODO Implement in datafeed a generic save method
        # (which could call the correct database save method)
        # Get a portfolio monthly risk analyzis
        perf_series  = analyzes.rolling_performances(timestamp='one_month',
                                                     save=True,
                                                     db_id=configuration['database'])

        #TODO save returns not ready yet, don't try to save #TODO Becnhmark was
        # Get daily, cumulative and not, returns of portfolio and benchmark
        returns_df = analyzes.get_returns(
                benchmark=datautils.Exchange[configuration['exchange']]['index'],
                save=False)

        risk_metrics = analyzes.overall_metrics(metrics=perf_series,
                                                save=True,
                                                db_id=configuration['database'])

        #FIXME irrelevant results if no transactions were ordered
        utils.log.info('\n\nReturns: {}% / {}%\nVolatility: {} \
                \nSharpe:\t\t{}\nMax drawdown:\t{}\n\n'.format(
                risk_metrics['Returns'] * 100.0,
                risk_metrics['Benchmark.Returns'] * 100.0,
                risk_metrics['Volatility'],
                risk_metrics['Sharpe.Ratio'],
                risk_metrics['Max.Drawdown']))

        # If we work in local, draw a quick summary plot
        if not configuration['remote']:
            data = returns_df.drop(['Returns', 'Benchmark.Returns'], axis=1)
            data.plot()
            plt.show()

            # R statistical analyzes
            #TODO Wrap it in Analyze object using rpy or rest server
            os.system('{}/application/analysis.R --source mysql --table {} --verbose'
                    .format(os.environ['QTRADE'], configuration['database']))
            os.system('evince ./Rplots.pdf')


''' Notes
Strategies to swich strategies =)
Backtest the strategy on many datasets, and check correlations to test algorithm efficiecy
Cross validation

Manager hint
1.  a. Choose m stocks according to their best momentum or sharpe ratio for example
    b. Select n stocks from m according to portfolio optimization
'''
