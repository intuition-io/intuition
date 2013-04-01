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

""" Genetic Algorithmn Implementation """
import argparse
import pytz
from datetime import datetime

from neuronquant.gears.engine import Simulation
import neuronquant.algorithmic.optimizations.optimize as optimize
from neuronquant.utils import log, color_setup, remote_setup


#TODO Develop genetic specific functions (cf old class and methods choice)
#     Then Integrate more optimization functions on same model
#     Then store and analyse the data in database
class Metric(object):
    ''' Evaluate error of a solution in optimization '''
    def __init__(self):
        # General backtest behavior configuration
        self.configuration = {'algorithm'   : 'DualMA',
                         'frequency'       : 'daily',
                         'manager'     : 'Constant',
                         'database'    : 'test',
                         'tickers'     : ['google', 'apple'],
                         'start'       : pytz.utc.localize(datetime(2008, 1, 11)),
                         'end'         : pytz.utc.localize(datetime(2010, 7, 3)),
                         'live'        : False,
                         'port'        : '5570',
                         'cash'        : 100000,
                         'exchange'    : 'nasdaq',
                         'remote'      : False}

        # Object use to run zipline backtest
        self.engine = Simulation()

        # Configure and return data used during backtest, and the TradingEnvironement
        self.data, self.context = self.engine.configure(self.configuration)

    def fitness(self, genes):
        '''
        Cost function in the optimization process
        _________________________________________
        Parameters
            genes: list
                Parameters to optimize
        _________________________________________
        Return
            score: float
                Error of the cost function ran with this solution
                So the algo tries to minimize it (i.e. 0 is the best score)
        '''

        # No evoluation in manager (Constant) configuration
        # We try here to optimize the algorithm parameters
        strategie = {'manager': {'name': 'Xavier Bruhiere',
                                 'load_backup': 0,
                                 'max_weight': 0.4,
                                 'buy_amount': 200,
                                 'sell_amount': 100,
                                 'connected': 0},
                     'algorithm': {'long_window': int(genes[0]),
                                    'ma_rate': float(genes[1] / 10.0),
                                    'threshold': genes[2]}
                     }
        try:
            # Run backtest with all configuration dictionnaries
            analyzes = self.engine.run(self.data, self.configuration, strategie, self.context)

            # Get back summary performance dictionnary
            risk_metrics = analyzes.overall_metrics()
        except:
            import ipdb; ipdb.set_trace()
            log.error('Exception caught while running cost function')
            # Return worst result possible
            return 1

        return self.evaluate(risk_metrics)

    def evaluate(self, risks):
        '''
        Define score from raw cost function results
        '''
        score = [risks['Returns'], risks['Sharpe.Ratio'], risks['Max.Drawdown'], risks['Volatility']]

        # Debug purpose
        if score[0]:
            log.notice(risks)

        # Compute score from cummulative returns,
        return 1 - score[0]


if __name__ == "__main__":
    '''
    Quick and dirty interface for running
    genetic optimization process
    '''
    parser = argparse.ArgumentParser(description='Trading strategie optimization through genetic algorithm')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s v0.8.1 Licence rien du tout', help='Print program version')
    parser.add_argument('-p', '--popsize', type=int, action='store', default=10, required=False, help='number of chromosomes in a population')
    parser.add_argument('-e', '--elitism', type=float, action='store', default=0.2, required=False, help='% of best chromosomes kept as is for the next generation')
    parser.add_argument('-s', '--step', type=float, action='store', default=1.0, required=False, help='Mutation leverage')
    parser.add_argument('-i', '--iteration', type=int, action='store', default=20, required=False, help='Max number of evolution iteration')
    parser.add_argument('-m', '--mutation', type=float, action='store', default=0.5, required=False, help='Probability for a mutation to happen')
    parser.add_argument('-n', '--notify', action='store_true', help='Flag to send android notification')
    parser.add_argument('-r', '--remote', action='store_true', help='running mode, used for logging message endpoint')
    args = parser.parse_args()

    log_setup = (remote_setup if args.remote else color_setup)
    with log_setup.applicationbound():
        #TODO manage float parameters
        #NOTE A dico might be more readable
        #FIXME Step is the same whatever the parameter, scale issue
        score, best_parameters = optimize.genetic([(100, 200), (3, 9), (0, 20)],
                                                  Metric(),
                                                  popsize = args.popsize,
                                                  step    = args.step,
                                                  elite   = args.elitism,
                                                  maxiter = args.iteration,
                                                  mutprob = args.mutation,
                                                  notify_android=args.notify)

        log.notice('Best parameters evolved: {} -> {}'.format(best_parameters, score))
