#
# Copyright 2013 Xavier Bruhiere
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
from neuronquant.utils import LogSubsystem
from neuronquant.algorithmic.optimizations.genetic import Genetic, GeneticAlgorithm


def testGenetic(genes):
    '''--------------------------------------------    Parameters    -----'''
    '''chromosome[short_window, long_window, buy_on_event, sell_on_event] '''
    #print('chromosome: {}'.format(genes))
    '''-----------------------------------------------    Running    -----'''
    score = 0
    for gene in genes.values():
        score += gene
    return score


class EvolveQuant(Genetic):
    def __init__(self, evaluator, logger=None, elitism_rate=25,
                 prob_crossover=0.8, prob_mutation=0.2):
        self._logger = LogSubsystem(self.__class__.__name__, 'info').getLog()
        self._logger.info('Initiating genetic environment.')
        Genetic.__init__(self, evaluator, elitism_rate, prob_crossover,
                         prob_mutation, self._logger)

'''
Gene code description
long_window = 73 -> 200 : 0000000 > 1111111 + 73
ma_rate = 3 -> 10 : 000 > 111 + 2
buy_n = 10 -> 300 : 11111111 + 25
buy_rate = 37 -> 100 : 111111 + 37
'''

if __name__ == "__main__":
    ''' So a new algorithm needs a gene_description and an evaluator '''
    gene_code = {'short_window': (6, 73), 'ma_rate': (3, 3), 'buy_n': (8, 25), 'buy_rate': (6, 37)}
    ga = EvolveQuant(testGenetic, elitism_rate=30, prob_mutation=0.2)
    ga.describeGenome(gene_code, popN=400)
    GeneticAlgorithm(ga, selection='roulette').run(generations=100, freq=50)
