"""Genetic Algorithmn Implementation """
import random
import bisect
import sys
import os

sys.path.append(os.environ['QTRADE'])
from neuronquant.utils import LogSubsystem

# Default values, oviously...
#TODO some are in percent, others are decimals
CROSSOVER_DEFAULT   = 0.9
MUTATION_DEFAULT    = 0.02
ELITISM_DEFAULT     = 10
POPULATION_DEFAULT  = 80
GENERATIONS_DEFAULT = 100


#TODO roulette to chose and implement
def roulette2(fs):
    fs = [abs(score) for score in fs]
    n_rand = random.random() * sum(fs)
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
    #n_rand = random.random()*sum(fs)
    cfs = [sum(fs[:i + 1]) for i in xrange(len(fs))]
    select = bisect.bisect_left(cfs, random.uniform(0, cfs[-1]))
    #print('cfs: {}'.format(cfs))
    #print('Selected index {}'.format(select))
    return select


def roulette0(fs):
    #idx = 0
    cumulative_fitness = 0.0
    r = random.random()
    for i in range(len(fs)):
        cumulative_fitness += fs[i]
        if cumulative_fitness > r:
            return i


class GeneticAlgorithm(object):
    ''' population is a set of chromosomes'''
    def __init__(self, genetics, selection='roulette'):
        self._logger = LogSubsystem(self.__class__.__name__, 'debug').getLog()
        self._logger.info('Initiating genetic algorithm.')
        self.genetics = genetics
        self.selection = selection

    def run(self, generations=10, freq=10):
        self._logger.info('Running genetic algorithm')
        self._logger.info('Generating random population')
        population = self.genetics.generatePopulation()
        self._logger.debug('Initial population: {}'.format(population))
        while True:
            fits_pops = sorted([(self.genetics.fitness(ch), ch) for ch in population], reverse=True)
            if self.genetics.checkStop(fits_pops, generations, freq):
                break
            population = self.iteratePopulation(fits_pops)
        return population

    def rouletteWheel(self, fitness_scores, ranked_chromos):
        while True:
            idx1 = roulette(fitness_scores)
            idx2 = roulette(fitness_scores)
            if idx1 == idx2:
                continue
            else:
                break
        #self._logger.debug('Index [{},{}] selected'.format(idx1, idx2))
        return [ranked_chromos[idx1], ranked_chromos[idx2]]

    def iteratePopulation(self, ranked_pop):
        # This parents selection use tournement method
        #self._logger.info('Evolving population')
        if self.selection == 'tournament' or self.selection == 'sorted':
            parents_generator = self.genetics.parents(ranked_pop, self.selection)
        fitness_scores = [item[0] for item in ranked_pop]
        ranked_chromos = [item[-1] for item in ranked_pop]
        newpop = []
        newpop.extend(ranked_chromos[:int(round(self.genetics._elitismRate() * self.genetics.popN / 100))])  # Elitism
        while len(newpop) < self.genetics.popN:
            if self.selection == 'tournament' or self.selection == 'sorted':
                parents = next(parents_generator)
            elif self.selection == 'roulette':
                parents = self.rouletteWheel(fitness_scores, ranked_chromos)
            else:
                self._logger.error('** Selector not implemented, exiting')
                sys.exit(1)
            cross = random.random() < self.genetics._probabilityCrossover()
            children = self.genetics.crossover(parents) if cross else parents
            for ch in children:
                #mutate = random.random() < self.genetics._probabilityMutation()
                #newpop.append(self.genetics.mutation(ch) if mutate else ch)
                ch = self.genetics.mutate(ch)
                newpop.append(ch)
        return newpop


class Genetic(object):
    def __init__(self, evaluator, elitism_rate=ELITISM_DEFAULT, prob_crossover=CROSSOVER_DEFAULT,
                 prob_mutation=MUTATION_DEFAULT, target=None):
        self._logger = LogSubsystem(self.__class__.__name__, 'debug').getLog()
        self.target = target
        self.counter = 0
        self.evaluator = evaluator
        self.elitism_rate = elitism_rate
        self.prob_crossover = prob_crossover
        self.prob_mutation = prob_mutation

    def describeGenome(self, gene_code, popN=POPULATION_DEFAULT):
        self._logger.info('Generating population of described genome')
        self.popN = popN
        self.gene_code = gene_code

    def decode(self, chromosome):
        start      = 0
        gene       = dict()
        chromo_str = ''.join([str(bit) for bit in chromosome])
        for key in self.gene_code.keys():
            gene_str  = chromo_str[start:start + self.gene_code[key][0]]
            gene[key] = int(gene_str, 2) + self.gene_code[key][1]
            start     = len(gene_str)
        return gene

    def generatePopulation(self):
        return [self._randomChromosome() for j in range(self.popN)]

    def _randomChromosome(self):
        len_chromo = sum([self.gene_code[key][0] for key in self.gene_code])
        test = [random.randint(0, 1) for i in range(len_chromo)]
        return test

    def fitness(self, chromosome):
        genes = self.decode(chromosome)
        return self.evaluator(genes)

    #TODO other stop conditions
    def checkStop(self, fits_populations, generations=GENERATIONS_DEFAULT, freq=10):
        self._logger.debug('generations {} and freq {}'.format(generations, freq))
        self.counter += 1
        if self.counter % (round(generations / freq)) == 0:
            best_match = list(sorted(fits_populations))[-1][1]
            fits = [f for f, ch in fits_populations]
            best = max(fits)
            worst = min(fits)
            ave = sum(fits) / len(fits)
            self._logger.info('[G %3d] score=(%4f, %4f, %4f): %r' %
                (self.counter, best, ave, worst, best_match))
        return self.counter >= generations

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
            self._logger.error('** Type selection not implemented: {}'.format(type))
        return

    def crossover(self, parents, type='single'):
        father, mother = parents
        index1 = random.randint(1, len(father) - 2)
        if type == 'double':
            index2 = random.randint(1, len(father) - 2)
            if index1 > index2:
                index1, index2 = index2, index1
            child1 = father[:index1] + mother[index1:index2] + father[index2:]
            child2 = mother[:index1] + father[index1:index2] + mother[index2:]
            return (child1, child2)
        elif type == 'single':
            return (father[:index1] + mother[index1:], mother[:index1] + father[index1:])
        else:
            self._logger.error('** Crossover type not implemented: {}'.format(type))
            raise NotImplementedError()
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
            sensitivity = 40
            for idx in range(len(chromosome)):
                if random.random() < self._probabilityMutation():
                    variation = random.randint(-sensitivity, sensitivity)
                    chromosome[idx] += variation
            # Contraintes
            while chromosome[0] > chromosome[1] / 2:
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
            self._logger.error('** Mutation type not implemented: {}'.format(type))
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
        return fits_populations[random.randint(0, len(fits_populations) - 1)]


''' binary
2 solutions of genetic code:
    [34 ... 45] <=> [0011, ...,  1010] + offset
bin_x_str = bin(x)[:2]
int_x = int(bin_x_str, 2)
tactique:
genetic code = list of str binaries expression
chromosome = [01011 011 100]  (3 genes here)
genes_dict = decode(chromosome)
'''
