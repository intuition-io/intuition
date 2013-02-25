#!/usr/bin/python
# encoding: utf-8

"""Genetic Algorithmn Implementation """
import ipdb as pdb

import sys
import os

sys.path.append(os.environ['QTRADE'])
from neuronquant.calculus.engine import Simulation
from neuronquant.ai.genetic import Genetic, GeneticAlgorithm
from neuronquant.ai.optimize import genetic_optimize
from neuronquant.utils import log, color_setup

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

#data = DataFeed().quotes(global_bt_cfg['tickers'],
                         #start_date=global_bt_cfg['start'],
                         #end_date=global_bt_cfg['end'])
#engine = Simulation(data)


def evaluate_backtest(genes):
    '''--------------------------------------------    Parameters    -----'''
    '''chromosome[short_window, long_window, buy_on_event, sell_on_event]
    log.debug('chromosome: {}'.format(genes))
    short_window  = genes['short_window']
    long_window   = round(short_window * genes['ma_rate'] / 2)
    buy_on_event  = genes['buy_n']
    sell_on_event = round(buy_on_event * genes['buy_rate'] / 100)
    '''
    #FIXME float encoding screws the idea
    #genes['ma_rate'] = float(genes['ma_rate']) / 10.0
    genes[1] = float(genes[1]) / 10.0

    '''-----------------------------------------------    Running    -----'''
    # No evoluation in manager (Constant) configuration so reads it statically from file
    # We want here to optimize the algorithm parameters
    engine = Simulation()
    #engine.configure(bt_cfg=global_bt_cfg, a_cfg=genes, m_cfg=None)
    engine.configure(bt_cfg=global_bt_cfg, a_cfg={'long_window': genes[0], 'ma_rate': genes[1], 'threshold': genes[2]}, m_cfg=None)
    results = engine.run_backtest()

    risk_metrics = engine.overall_metrics()
    score = [risk_metrics['Returns'], risk_metrics['Sharpe.Ratio'], risk_metrics['Max.Drawdown'], risk_metrics['Volatility']]
    score = [results['portfolio_value'][-1], results['pnl'].cumsum()[-1], (results['returns'] + 1).cumprod()[-1]]

    score = score[0]
    log.info('-----------> Returns performance: {}'.format(score))
    return score


class EvolveQuant(Genetic):
    def __init__(self, evaluator, elitism_rate=10,
                 prob_crossover=0.8, prob_mutation=0.2):
        Genetic.__init__(self, evaluator, elitism_rate, prob_crossover, prob_mutation)

'''
Gene code description {'name': [length_bit_code, offset], ...}
long_window = 73 -> 200 : 0000000 > 1111111 + 73
ma_rate = 3 -> 10 : 000 > 111 + 2
buy_n = 10 -> 300 : 11111111 + 25
buy_rate = 37 -> 100 : 111111 + 37
'''

if __name__ == "__main__":
    with color_setup.applicationbound():
        ''' So a new algorithm needs a gene_description and an evaluator '''
        #TODO enter the possible values
        #gene_code = {'long_window': [7, 73], 'ma_rate': [3, 3], 'threshold': [3, 0]}
        #ga = EvolveQuant(evaluate_backtest, elitism_rate=0.4)
        #ga.describeGenome(gene_code, popN=5)
        #GeneticAlgorithm(ga, selection='roulette').run(generations=5, freq=1)

        #TODO float parameters handler
        #NOTE A dico would be more readable
        best_parameters = genetic_optimize([(100, 200), (3, 10), (0, 20)], evaluate_backtest,
                                           popsize=10, step=4, elite=0.3, maxiter=10, mutprob=0.3)
        print('Best parameters evolved: {}'.format(best_parameters))
