"""Genetic Algorithmn Implementation """
import random, bisect

import sys, os

import matplotlib.pyplot as plt

sys.path.append(str(os.environ['QTRADE']))
from pyTrade.data.DataAgent import DataAgent
from pyTrade.compute.Algorithms import Backtester 
import pandas as pd
import pytz

from zipline.data.benchmarks import *

start = pd.datetime(2008,6,20, 0, 0, 0, 0, pytz.utc)
end = pd.datetime(2010,4,1, 0, 0, 0, 0, pytz.utc)
delta = pd.datetools.timedelta(days=1)

dataobj = DataAgent('stocks.db')
data_tmp = dataobj.getQuotes(['altair'], ['open'], \
        start=start, end=end, delta=delta, reverse=True)
data = data_tmp['open']

def runBacktest(genes):
    '''--------------------------------------------    Parameters    -----'''
    '''chromosome[short_window, long_window, buy_on_event, sell_on_event] '''
    print('chromosome: {}'.format(genes))
    short_window = genes['short_window']
    long_window = short_window * genes['ma_rate'] / 2
    buy_on_event = genes['buy_n'] 
    sell_on_event = round(buy_on_event * genes['buy_rate'] / 100)
    '''-----------------------------------------------    Running    -----'''
    print('\n-- Running backetester, algorithm: {}\n'.format('DualMA'))
    strategie = Backtester('DualMA', short_window=short_window, long_window=long_window, \
            amount=50000, buy_on_event=buy_on_event, sell_on_event=sell_on_event)
    results = strategie.run(data, start, end)
    score = strategie.portfolio.returns
    print('-------------------------------------> Returns performance: {}'.format(score))
    return score

''' binary
2 solutions of genetic code:
    [34 ... 45] <=> [0011, ...,  1010] + offset
bin_x_str = bin(x)[:2]
int_x = int(bin_x_str, 2)
tactique:
genetic code = list of str binaries expression
chromosome = [01011 011 100]  (3 genes here)
genes_dict = translate(chromosome)
'''

gene = dict()
gene_code = {'short_window': (6,73), 'ma_rate': (3,3), 'buy_n': (8,25), 'buy_rate': (6,37)}
''' 
long_window = 73 -> 200 : 0000000 > 1111111 + 73
ma_rate = 3 -> 10 : 000 > 111 + 2
buy_n = 10 -> 300 : 11111111 + 25
buy_rate = 37 -> 100 : 111111 + 37
'''

def translate(chromosome):
    start=0
    chromo_str = ''.join([str(bit) for bit in chromosome])
    for key in gene_code.keys():
        gene_str = chromo_str[start:start+gene_code[key][0]]
        gene[key] = int(gene_str, 2) + gene_code[key][1]
        start = len(gene_str)
    return gene
    

def roulette2(fs):
    fs = [abs(score) for score in fs]
    n_rand = random.random()*sum(fs)
    sum_fit = 0
    for i in range(len(fs)):
        sum_fit += fs[i]
        if sum_fit >= n_rand:
            break
    #print('Debug, scores: {}'.format(fs))
    #print('Selected index {}'.format(i))
    return i

def roulette3(fs):
    fs = [abs(score) for score in fs]
    p = random.uniform(0, sum(fs))
    for i, f in enumerate(fs):
        if p <= 0:
            break
        p -= f
    return i

def roulette(fs):
    fs = [abs(score) for score in fs]
    n_rand = random.random()*sum(fs)
    cfs = [sum(fs[:i+1]) for i in xrange(len(fs))]
    select = bisect.bisect_left(cfs, random.uniform(0, cfs[-1]))
    #print('cfs: {}'.format(cfs))
    #print('Selected index {}'.format(select))
    return select

def roulette0(fs):
    idx = 0
    cumulative_fitness = 0.0
    r = random.random()
    for i in range(len(fs)):
        cumulative_fitness += fs[i]
        if cumulative_fitness > r:
            return i

class GeneticAlgorithm(object):
    ''' population is a set of chromosomes'''
    def __init__(self, genetics):
        self.genetics = genetics

    def run(self):
        population = self.genetics.generatePopulation()
        print('Initial population: {}'.format(population))
        while True:
            fits_pops = sorted([(self.genetics.fitness(ch),  ch) \
                    for ch in population], reverse=True)
            if self.genetics.checkStop(fits_pops): break
            population = self.iteratePopulation(fits_pops)
            pass
        return population

    def selectFittest(self, fitness_scores, ranked_chromos):
        while True:
            idx1 = roulette(fitness_scores)
            idx2 = roulette(fitness_scores)
            if idx1 == idx2:
                continue
            else:
                break
        #print('[{},{}] selected'.format(idx1, idx2))
        return [ranked_chromos[idx1], ranked_chromos[idx2]]

    def iteratePopulation(self, ranked_pop):
        # This parents selection use tournement method
        #parents_generator = self.genetics.parents(ranked_pop)
        fitness_scores = [item[0] for item in ranked_pop]
        ranked_chromos = [item[-1] for item in ranked_pop]
        newpop = []
        newpop.extend(ranked_chromos[:int(round(self.genetics._elitismRate() * self.genetics.popN/100))])  # Elitism
        while len(newpop) < self.genetics.popN:
            #parents = next(parents_generator)
            parents = self.selectFittest(fitness_scores, ranked_chromos)
            cross = random.random() < self.genetics._probabilityCrossover()
            children = self.genetics.crossover(parents) if cross else parents
            for ch in children:
                #mutate = random.random() < self.genetics._probabilityMutation()
                #newpop.append(self.genetics.mutation(ch) if mutate else ch)
                ch = self.genetics.mutate(ch)
                newpop.append(ch)
        return newpop


class optimizeBacktest(object):
    def __init__(self, target_return,
                 limit=10, popN=4, elitism_rate=25,
                 prob_crossover=0.8, prob_mutation=0.2):
        self.target = target_return
        self.counter = 0
        self.limit = limit
        self.popN = popN
        self.elitism_rate = elitism_rate
        self.prob_crossover = prob_crossover
        self.prob_mutation = prob_mutation
        pass

    def generatePopulation(self):
        return [self._randomChromo() for j in range(self.popN)]

    def _randomChromo(self):
        len_chromo = sum([gene_code[key][0] for key in gene_code])
        test = [random.randint(0, 1) for i in range(len_chromo)]
        return test

    def fitness(self, chromosome):
        genes = translate(chromosome)
        return runBacktest(genes)

    #TODO other stop conditions
    def checkStop(self, fits_populations):
        self.counter += 1
        if self.counter % (self.limit/10) == 0:
            best_match = list(sorted(fits_populations))[-1][1]
            fits = [f for f, ch in fits_populations]
            best = max(fits)
            worst = min(fits)
            ave = sum(fits) / len(fits)
            print(
                "[G %3d] score=(%4f, %4f, %4f): %r" %
                (self.counter, best, ave, worst, best_match))
            pass
        return self.counter >= self.limit

    def parents(self, fits_populations, type='tournament'):
        if type == 'sorted':
            gen = iter(sorted(fits_populations))
            while True:
                f1, ch1 = next(gen)
                f2, ch2 = next(gen)
                yield (ch1, ch2)
        elif type == 'tournament':
            while True:
                father = self._tournament(fits_populations)
                mother = self._tournament(fits_populations)
                yield (father, mother)
        else:
            print('Type selection not implemented: {}'.format(type))
        return

    def crossover(self, parents, type='single'):
        father, mother = parents
        index1 = random.randint(1, len(father) - 2)
        if type == 'double':
            index2 = random.randint(1, len(father) - 2)
            if index1 > index2: index1, index2 = index2, index1
            child1 = father[:index1] + mother[index1:index2] + father[index2:]
            child2 = mother[:index1] + father[index1:index2] + mother[index2:]
            return (child1, child2)
        elif type == 'single':
            return (father[:index1]+mother[index1:], mother[:index1]+father[index1:])
        else:
            print('Type not implemented')
        return (None, None)

    def mutate(self, chromosome, type='binarie'):
        if type == 'binarie':
            mutated_ch = []
            for idx in chromosome:
                if random.random() < self._probabilityMutation():
                    if idx == 1:
                        mutated_ch.append(0)
                    else:
                        mutated_ch.append(1)
                else:
                    mutated_ch.append(idx)
            return mutated_ch
        elif type == 'real':
            sensitivity=40
            for idx in range(len(chromosome)):
                if random.random() < self._probabilityMutation():
                    variation = random.randint(-sensitivity, sensitivity)
                    chromosome[idx] += variation
            # Contraintes
            while chromosome[0] > chromosome[1]/2:
                chromosome[0] -= 1
            return chromosome
        elif type == 'single':
            sensitivity = 40
            index = random.randint(0, len(chromosome) - 1)
            vary = random.randint(-sensitivity, sensitivity)
            mutated = list(chromosome)
            mutated[index] += vary
            return mutated
        else:
            print('** Mutation type not implemented: {}'.format(type))
        return chromosome

    # internals
    def _elitismRate(self):
        r"""returns rate of occur crossover(0.0-1.0)"""
        return self.elitism_rate

    def _probabilityCrossover(self):
        r"""returns rate of occur crossover(0.0-1.0)"""
        return self.prob_crossover

    def _probabilityMutation(self):
        r"""returns rate of occur mutation(0.0-1.0)"""
        return self.prob_mutation

    def _tournament(self, fits_populations):
        alicef, alice = self._select_random(fits_populations)
        bobf, bob = self._select_random(fits_populations)
        return alice if alicef > bobf else bob

    def _select_random(self, fits_populations):
        return fits_populations[random.randint(0, len(fits_populations)-1)]

if __name__ == "__main__":
    GeneticAlgorithm(optimizeBacktest(20, prob_mutation=0.8)).run()
