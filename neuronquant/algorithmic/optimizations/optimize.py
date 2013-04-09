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


import random
import math
import numpy as np

import logbook
log = logbook.Logger('Optimization')

from neuronquant.network.transport import ZMQ_Dealer


def randomoptimize(domain, costf):
    best = 999999999
    bestr = None
    for i in range(0, 1000):
        # create a random solution
        r = [float(random.randint(domain[i][0], domain[i][1])) for i in range(len(domain))]

        # get the cost
        cost = costf(r)

        # compare it to the best one so far
        if cost < best:
            best = cost
            bestr = r
    return bestr


def hillclimb(domain, costf):
    # create a random solution
    sol = [random.randint(domain[i][0], domain[i][1])
           for i in range(len(domain))]
    # main loop
    while 1:
        # create list of neighboring solutions
        neighbors = []

        for j in range(len(domain)):
            # one away in each direction
            if sol[j] > domain[j][0]:
                neighbors.append(sol[0:j] + [sol[j] + 1] + sol[j + 1:])
            if sol[j] < domain[j][1]:
                neighbors.append(sol[0:j] + [sol[j] - 1] + sol[j + 1:])

        # see what the best solution amongst the neighbors is
        current = costf(sol)
        best = current
        for j in range(len(neighbors)):
            cost = costf(neighbors[j])
            if cost < best:
                best = cost
                sol = neighbors[j]

        # if there's no improvement, then we've reached the top
        if best == current:
            break
    return sol


def annealingoptimize(domain, costf, T=10000.0, cool=0.95, step=1):
    # initialize the values randomly
    vec = [float(random.randint(domain[i][0], domain[i][1]))
           for i in range(len(domain))]

    while T > 0.1:
        # choose one of the indices
        i = random.randint(0, len(domain) - 1)

        # choose a direction to change it
        dir = random.randint(-step, step)

        # create a new list with one of the values changed
        vecb = vec[:]
        vecb[i] += dir
        if vecb[i] < domain[i][0]:
            vecb[i] = domain[i][0]
        elif vecb[i] > domain[i][1]:
            vecb[i] = domain[i][1]

        # calculate the current cost and the new cost
        ea = costf(vec)
        eb = costf(vecb)
        p = pow(math.e, (-eb - ea) / T)

        # Is it better, or does it make the probability
        # cutoff?
        if (eb < ea or random.random() < p):
            vec = vecb

        # Decrease the temperature
        T = T * cool
    return vec


def genetic(domain, cost_obj, popsize=50, step=1,
                     mutprob=0.2, elite=0.2, maxiter=100, stop=0, notify_android=False):
    '''
    Parameter optimization using genetic algorithm
    ______________________________________________
    Parameters
        domain: vec(...) of tuple(2)
            define range for each parameter
        cost_obj: Metric(1)
            compute the score of a solution
        popsize: int(1)
            number of solution set in one generation
        step: float(1)
            sensibility used while mutating a parameter
        mutprob: float(1)
            probability for a solution to mutate
        elite: float(1)
            % of best chromosomes selected
        maxiter: int(1)
            maximum number of population evolution
        stop: float(1)
            stop the algorithm when the fitness function reachs this value
        notify_android: bool(1)
            flag that let you send a notificatioin on android device when the algo is done
    ______________________________________________
    Return
        scores[0][0]: float(1)
            Best score the algorithm reached
        scores[0][1]: vec(...) of float(1)
           parameters that gave the best score
    '''
    # Initialisation
    client = ZMQ_Dealer(id=genetic.__name__)
    client.run(host='127.0.0.1', port=5570)
    check_buffer = [1] * 4

    # Mutation Operation
    def mutate(vec):
        i = random.randint(0, len(domain) - 1)
        if random.random() < 0.5 and vec[i] > domain[i][0]:
            mutated_param = vec[i] - step if vec[i] - step >= domain[i][0] else domain[i][0]
        elif vec[i] < domain[i][1]:
            mutated_param = vec[i] + step if vec[i] + step <= domain[i][0] else domain[i][0]
        return vec[0:i] + [mutated_param] + vec[i + 1:]

    # Crossover Operation
    def crossover(r1, r2):
        i = random.randint(1, len(domain) - 2)
        return r1[0:i] + r2[i:]

    def should_stop(best):
        ''' Break the loop if no longer evolution, or reached stop criteria '''
        check_buffer.append(best)
        check_buffer.pop(0)
        return (best >= check_buffer[0]) or (best <= stop)

    log.info('Build the initial population')
    pop = []
    for i in range(popsize):
        vec = [random.randint(domain[i][0], domain[i][1])
               for i in range(len(domain))]
        pop.append(vec)

    # How many winners from each generation?
    topelite = int(elite * popsize)

    log.info('Run main loop')
    for i in range(maxiter):
        log.info('Rank population')
        scores = [(cost_obj.fitness(v), v) for v in pop]
        scores.sort()
        ranked = [v for (s, v) in scores]

        # Start with the pure winners
        log.info('Select elite')
        pop = ranked[0:topelite]

        # Add mutated and bred forms of the winners
        log.info('Evolve loosers')
        while len(pop) < popsize:
            if random.random() < mutprob:
                log.debug('Process mutation')
                c = random.randint(0, topelite)
                pop.append(mutate(ranked[c]))
            else:
                log.debug('Process crossover')
                c1 = random.randint(0, topelite)
                c2 = random.randint(0, topelite)
                pop.append(crossover(ranked[c1], ranked[c2]))

        #TODO add worst
        log.error(scores)
        log.notice('Best score so far: {}'.format(scores[0][0]))
        client.send({'best': scores[0],
                     'worst': scores[-1],
                     'parameters': scores[0][1],
                     'mean': np.mean([s[0] for s in scores]),
                     'std': np.std([s[0] for s in scores]),
                     'iteration': i + 1,
                     'progress': round(float(i + 1) / float(maxiter), 2) * 100.0},
                     type='optimization',
                     channel='dashboard')
        if should_stop(scores[0][0]):
            log.info('Stop criteria reached, done with optimization.')
            break

    if notify_android:
        client.send_to_android({'title': 'Optimization is done',
                                'priority': 1,
                                'description': 'Genetic algorithm evolved the solution to {} \
                                               (with parameters {})'.format(scores[0][0], scores[0][1])})
    return scores[0][0], scores[0][1]
