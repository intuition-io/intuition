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

"""Genetic Algorithmn Implementation """
import random
import bisect

import sys
import os

import matplotlib.pyplot as plt

sys.path.append(str(os.environ['QTRADE']))
from pyTrade.data.DataAgent import DataAgent
from pyTrade.calculus.engine import Backtester
from pyTrade.utils import LogSubsystem
import pandas as pd
import pytz

from zipline.data.benchmarks import *

from pyTrade.ai.genetic import Genetic, GeneticAlgorithm

start    = pd.datetime(2008, 6, 20, 0, 0, 0, 0, pytz.utc)
end      = pd.datetime(2010, 4, 1, 0, 0, 0, 0, pytz.utc)
delta    = pd.datetools.timedelta(days = 1)

dataobj  = DataAgent('stocks.db')
data_tmp = dataobj.getQuotes(['google'], ['open'],
                                  start=start,
                                  end=end,
                                  delta=delta,
                                  reverse = True)
data     = data_tmp['open']


def runBacktest(genes):
    '''--------------------------------------------    Parameters    -----'''
    '''chromosome[short_window, long_window, buy_on_event, sell_on_event] '''
    print('chromosome: {}'.format(genes))
    short_window  = genes['short_window']
    long_window   = round(short_window * genes['ma_rate'] / 2)
    buy_on_event  = genes['buy_n']
    sell_on_event = round(buy_on_event * genes['buy_rate'] / 100)
    '''-----------------------------------------------    Running    -----'''
    print('\n-- Running backetester, algorithm: {}\n'.format('DualMA'))
    strategie = Backtester('DualMA',
                           short_window=short_window,
                           long_window=long_window,
                           amount=50000,
                           buy_on_event=buy_on_event,
                           sell_on_event=sell_on_event)
    #results = strategie.run(data, start, end)
    score   = strategie.portfolio.returns
    print('-------------------------------------> Returns performance: {}'.format(score))
    return 30 + score


class EvolveQuant(Genetic):
    def __init__(self, evaluator, elitism_rate=10,
                 prob_crossover=0.8, prob_mutation=0.2):
        self._logger = LogSubsystem(self.__class__.__name__, 'debug').getLog()
        self._logger.info('Initiating genetic environment.')
        Genetic.__init__(self, evaluator, elitism_rate, prob_crossover, prob_mutation, logger)

'''
Gene code description
long_window = 73 -> 200 : 0000000 > 1111111 + 73
ma_rate = 3 -> 10 : 000 > 111 + 2
buy_n = 10 -> 300 : 11111111 + 25
buy_rate = 37 -> 100 : 111111 + 37
'''

if __name__ == "__main__":
    ''' So a new algorithm needs a gene_description and an evaluator '''
    #TODO enter the possible values
    gene_code = {'short_window': (6, 73), 'ma_rate': (3, 3), 'buy_n': (8, 25), 'buy_rate': (6, 37)}
    ga = EvolveQuant(runBacktest, elitism_rate=40)
    ga.describeGenome(gene_code, popN=40)
    GeneticAlgorithm(ga, selection='roulette').run(generations=50, freq=50)
