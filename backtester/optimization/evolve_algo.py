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

#NOTE Could run the script like any backtest, with a --optimization parameter ??
global_bt_cfg = {'algorithm'   : 'DualMA',
                 'delta'       : 'D',
                 'manager'     : 'Constant',
                 'database'    : None,
                 'tickers'     : ['google', 'apple'],
                 'start'       : '2008-01-10',
                 'end'         : '2010-07-03',
                 'live'        : False,
                 'port'        : '5570',
                 'remote'      : False}


#TODO A class with __init__, fitness and evaluate metthods
#     Then Logging configuration (should be able to choose at least if it's remote from the remote client !)
#     Then write generic workerNode to make modules (with forwarder and console client) re-usuable
#     Then develop genetic function (cf old class and methods choice)
#     Then Integrate more optimization functions on same model
#     Then store and analyse the data in database
def evaluate_backtest(genes):
    '''
    @summary Cost function in the optimization process
    @args genes: vector of parameters or dict, depending of the algos used (tie break very soon)
    '''
    '''
    genes = [long_window, ma_rate, threshold]
    or:
    genes = {'long_window': 200, 'ma_rate': 3, 'threshold': 10}
    '''

    '''-----------------------------------------------    Running    -----'''
    # No evoluation in manager (Constant) configuration so reads it statically from file
    # We want here to optimize the algorithm parameters
    engine = Simulation()
    try:
        #engine.configure(bt_cfg=global_bt_cfg, a_cfg=genes, m_cfg=None)
        engine.configure(bt_cfg=global_bt_cfg, a_cfg={'long_window': genes[0], 'ma_rate': float(genes[1] / 10.0), 'threshold': genes[2]}, m_cfg=None)
        results = engine.run_backtest()
    except:
        pdb.set_trace()

    risk_metrics = engine.overall_metrics()
    log.notice(risk_metrics)
    score = [risk_metrics['Returns'], risk_metrics['Sharpe.Ratio'], risk_metrics['Max.Drawdown'], risk_metrics['Volatility']]
    log.notice([results['portfolio_value'][-1], results['pnl'].cumsum()[-1], (results['returns'] + 1).cumprod()[-1]])

    score = 1 - score[0]
    return score


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Trading strategie optimization through genetic algorithm')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s v0.8.1 Licence rien du tout', help='Print program version')
    parser.add_argument('-p', '--popsize', type=int, action='store', default=10, required=False, help='number of chromosomes in a population')
    parser.add_argument('-e', '--elitism', type=float, action='store', default=0.2, required=False, help='% of best chromosomes keep as is for the next generation')
    parser.add_argument('-s', '--step', type=float, action='store', default=1.0, required=False, help='Mutation leverage')
    parser.add_argument('-i', '--iteration', type=int, action='store', default=20, required=False, help='Max number of evolution iteration')
    parser.add_argument('-m', '--mutation', type=float, action='store', default=0.5, required=False, help='Probability for a mutation to happen')
    parser.add_argument('-n', '--notify', action='store_true', help='Flag to send android notification')
    args = parser.parse_args()

    with remote_setup.applicationbound():
        ''' So a new algorithm needs a gene_description and an evaluator '''
        #TODO float parameters handler
        #NOTE A dico would be more readable
        #NOTE Step is the same whatever the parameter, scale issue
        score, best_parameters = genetic_optimize([(100, 200), (3, 9), (0, 20)],
                                                  evaluate_backtest,
                                                  popsize=args.popsize,
                                                  step=args.step,
                                                  elite=args.elitism,
                                                  maxiter=args.iteration,
                                                  mutprob=args.mutation,
                                                  notify_android=args.notify)
        print('Best parameters evolved: {} -> {}'.format(best_parameters, score))
