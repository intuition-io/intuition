#!/usr/bin/python
# encoding: utf-8

""" Genetic Algorithmn Implementation """
import ipdb as pdb
import sys
import os
import argparse

sys.path.append(os.environ['QTRADE'])
from neuronquant.calculus.engine import Simulation
from neuronquant.ai.optimize import genetic_optimize
from neuronquant.utils import log, color_setup, remote_setup


#TODO A class with __init__, fitness and evaluate metthods
#     Then Logging configuration (should be able to choose at least if it's remote from the remote client !)
#     Then write generic workerNode to make modules (with forwarder and console client) re-usuable
#     Then develop genetic function (cf old class and methods choice)
#     Then Integrate more optimization functions on same model
#     Then store and analyse the data in database
class Metric(object):
    ''' Evaluate error of a solution in optimization '''
    def __init__(self):
        #TODO Instanciation and data should go here
        self.bt_cfg = {'algorithm'   : 'DualMA',
                         'delta'       : 'D',
                         'manager'     : 'Constant',
                         'database'    : None,
                         'tickers'     : ['google', 'apple'],
                         'start'       : '2008-01-11',
                         'end'         : '2010-07-03',
                         'live'        : False,
                         'port'        : '5570',
                         'remote'      : False}

    def fitness(self, genes):
        '''
        Cost function in the optimization process
        _________________________________________
        Parameters
            genes: list(3)
                ordered parameters to optimize
        _________________________________________
        Return
            score: float(1)
                Error of the cost function ran with this solution
        '''

        # No evoluation in manager (Constant) configuration so reads it statically from file
        # We want here to optimize the algorithm parameters
        engine = Simulation()
        try:
            engine.configure(bt_cfg=self.bt_cfg,
                             a_cfg={'long_window': genes[0], 'ma_rate': float(genes[1] / 10.0), 'threshold': genes[2]},
                             m_cfg=None)
            results = engine.run_backtest()
            risk_metrics = engine.overall_metrics()
        except:
            pdb.set_trace()
            log.error('Exception caught while running cost function')
            return 1

        return self.evaluate(results, risk_metrics)

    def evaluate(self, results, risks):
        '''
        Define score from raw cost function results
        '''
        score = [risks['Returns'], risks['Sharpe.Ratio'], risks['Max.Drawdown'], risks['Volatility']]
        if score[0]:
            log.notice(risks)
            log.notice([results['portfolio_value'][-1], results['pnl'].cumsum()[-1], (results['returns'] + 1).cumprod()[-1]])

        return 1 - score[0]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Trading strategie optimization through genetic algorithm')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s v0.8.1 Licence rien du tout', help='Print program version')
    parser.add_argument('-p', '--popsize', type=int, action='store', default=10, required=False, help='number of chromosomes in a population')
    parser.add_argument('-e', '--elitism', type=float, action='store', default=0.2, required=False, help='% of best chromosomes kept as is for the next generation')
    parser.add_argument('-s', '--step', type=float, action='store', default=1.0, required=False, help='Mutation leverage')
    parser.add_argument('-i', '--iteration', type=int, action='store', default=20, required=False, help='Max number of evolution iteration')
    parser.add_argument('-m', '--mutation', type=float, action='store', default=0.5, required=False, help='Probability for a mutation to happen')
    parser.add_argument('-n', '--notify', action='store_true', help='Flag to send android notification')
    args = parser.parse_args()

    with remote_setup.applicationbound():
        #TODO float parameters handler
        #NOTE A dico would be more readable
        #NOTE Step is the same whatever the parameter, scale issue
        score, best_parameters = genetic_optimize([(100, 200), (3, 9), (0, 20)],
                                                  Metric(),
                                                  popsize=args.popsize,
                                                  step=args.step,
                                                  elite=args.elitism,
                                                  maxiter=args.iteration,
                                                  mutprob=args.mutation,
                                                  notify_android=args.notify)
        log.notice('Best parameters evolved: {} -> {}'.format(best_parameters, score))
