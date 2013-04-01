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
import argparse

import matplotlib.pyplot as plt

sys.path.append(str(os.environ['QTRADE']))
from neuronquant.data.DataAgent import DataAgent
from neuronquant.calculus.Algorithms import Backtester
import pytz
import pandas as pd

from zipline.data.benchmarks import *

from pyevolve import G1DList, GSimpleGA, Selectors, logEnable
from pyevolve import Initializators, Mutators, Scaling, Consts

target_return = 20

start = pd.datetime(2008, 6, 20, 0, 0, 0, 0, pytz.utc)
end = pd.datetime(2010, 4, 1, 0, 0, 0, 0, pytz.utc)
delta = pd.datetools.timedelta(days=1)

dataobj = DataAgent('stocks.db')
data_tmp = dataobj.getQuotes(['altair'], ['open'],
                             start=start,
                             end=end,
                             delta=delta,
                             reverse=True)
data = data_tmp['open']
print data.head()
print(20 * '-')
#data.index = data.index.tz_localize(pytz.utc)


def evolveCallback(ga_engine):
    generation = ga_engine.getCurrentGeneration()
    if generation % 1 == 0:
        print "Current generation: %d" % (generation,)
        print ga_engine.getStatistics()
    return False


def runBacktest(chromosome):
    '''--------------------------------------------    Parameters    -----'''
    '''chromosome[short_window, long_window, buy_on_event, sell_on_event] '''
    short_window = chromosome[0] * 10
    long_window = chromosome[1] * 10
    buy_on_event = chromosome[2] * 10
    sell_on_event = chromosome[3] * 10
    '''-----------------------------------------------    Running    -----'''
    print('\n-- Running backetester, algorithm: {}\n'.format('DualMA'))
    strategie = Backtester('DualMA', short_window=short_window, long_window=long_window,
                           amount=50000, buy_on_event=buy_on_event, sell_on_event=sell_on_event)
    #results = strategie.run(data, start, end)
    score = strategie.portfolio.returns
    print('-------------------------------------> Returns performance: {}'.format(round(10000.0 * score)))
    return round(10000.0 * score)


if __name__ == '__main__':
    '''---------------------------------------------------------------------------------------'''
    genome = G1DList.G1DList(4)
    genome.setParams(rangemin=5, rangemax=20, roundDecimal=2,
                     bestrawscore=target_return)
    genome.initializator.set(Initializators.G1DListInitializatorInteger)
    #genome.mutator.set(Mutators.G1DListMutatorRealGaussian)
    genome.evaluator.set(runBacktest)
    ga = GSimpleGA.GSimpleGA(genome)
    ga.selector.set(Selectors.GRouletteWheel)
    #ga.setMinimax(Consts.minimaxType['minimize'])
    #ga.setPopulationSize(200)
    #ga.setGenerations(10)
    #ga.terminationCriteria.set(GSimpleGA.ConvergenceCriteria)
    ga.stepCallback.set(evolveCallback)
    ga.setElitism(True)
    pop = ga.getPopulation()
    pop.scaleMethod.set(Scaling.SigmaTruncScaling)

    ga.evolve(10)

    best = ga.bestIndividual()
    print "\nBest individual score: %.2f" % (best.score,)
    print best

    #score = runBacktest(args, short_window=40, long_window=80, buy_on_event=120, sell_on_event=80)

    '''---------------------------------------------------------------------------------------'''
