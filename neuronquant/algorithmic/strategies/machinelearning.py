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


from zipline.algorithm import TradingAlgorithm
import numpy as np
from sklearn.hmm import GaussianHMM
from zipline.transforms import batch_transform


HIDDEN_STATES = 3
INFINITE = np.inf


# Define batch transform which will be called
# periodically with a continuously updated array
# of the most recent trade data.
@batch_transform
def HMM(data, means_prior=None):
    # data is _not_ an event-frame, but an array
    # of the most recent trade events

    # Create scikit-learn model using the means
    # from the previous model as a prior
    #import ipdb; ipdb.set_trace()
    for sid in data['price'].columns:
        model = GaussianHMM(HIDDEN_STATES,
                            covariance_type="diag",
                            n_iter=10,
                            means_prior=means_prior,
                            means_weight=0.5)

        # Extract variation and volume
        diff = data.variation[sid].values
        volume = data.volume[sid].values
        X = np.column_stack([diff, volume])

        # Estimate model
        model.fit([X])

        return model


class PredictHiddenStates(TradingAlgorithm):
    def initialize(self, properties):
        # Instantiate batch_transform
        self.hmm_transform = HMM(refresh_period=properties.get('refresh_period', 300),  # recompute every 500 days
                                 window_length=properties.get('window_length', 100),
                                 #window_length=INFINITE,  # store all data
                                 compute_only_full=False)  # do not wait until window is full

        # State variables
        self.state = -1
        self.means_prior = None

    def handle_data(self, data):
        if not self.initialized:
            self.initialized = True
            for sid in data:
                data[sid]['variation'] = 0.0
            return
        # Pass event frame to batch_transform
        # Will _not_ directly call the transform but append
        # data to a window until full and then compute.
        self.hmm = self.hmm_transform.handle_data(data, means_prior=self.means_prior)

        # Have we fit the model yet?
        if self.hmm is None:
            return

        # Remember mean for the prior
        self.means_prior = self.hmm.means_

        for sid in data:
            data[sid]['variation'] = (data[sid].close_price - data[sid].open_price)

            # Predict current state
            data_vec = [data[sid].variation, data[sid].volume]
            self.state = self.hmm.predict([data_vec])
            self.record(state=self.state)

            self.logger.info(self.state)


# ___________________________________________________________________
import random


class StochasticGradientDescent(TradingAlgorithm):
    '''
    https://www.quantopian.com/posts/second-attempt-at-ml-stochastic-gradient-descent-method-using-hinge-loss-function
    '''
    def initialize(self, properties):
        self.save = properties.get('save', 0)
        #FIXME Should be set
        self.capital_base = properties.get('capital_base', 10000.0)
        self.bet_amount    = self.capital_base
        self.max_notional  = self.capital_base + 0.1
        self.min_notional  = -100000.0
        self.gradient_iterations = properties.get('gradient_iterations', 5)
        self.calculate_theta = calculate_theta(refresh_period=properties.get('refresh_period', 1),
                window_length=properties.get('window_length', 60))

    def handle_data(self, data):
        ''' ----------------------------------------------------------    Init   --'''
        if self.initialized:
            user_instruction = self.manager.update(
                    self.portfolio,
                    self.datetime.to_pydatetime(), 
                    self.perf_tracker.cumulative_risk_metrics.to_dict(),
                    save=self.save,
                    widgets=False)
        else:
            # Perf_tracker need at least a turn to have an index
            self.initialized = True

        for stock in data:
            thetaAndPrices = self.calculate_theta.handle_data(data, stock, self.gradient_iterations)
            if thetaAndPrices is None:
                continue

            theta, historicalPrices = thetaAndPrices

            # Indicator is a new manager !
            indicator = np.dot(theta, historicalPrices)
            # normalize
            hlen = sum([k * k for k in historicalPrices])
            tlen = sum([j * j for j in theta])
            indicator /= float(hlen * tlen)  # now indicator lies between [-1,1]

            current_Prices = data[stock].price
            notional = self.portfolio.positions[stock].amount * current_Prices

            if indicator >= 0 and notional < self.max_notional:
                self.order(stock, indicator * self.bet_amount)
                self.logger.notice("[%s] %f shares of %s bought." % (self.datetime, self.bet_amount * indicator, stock))

            if indicator < 0 and notional > self.min_notional:
                self.order(stock, indicator * self.bet_amount)
                self.logger.notice("[%s] %f shares of %s sold." % (self.datetime, self.bet_amount * indicator, stock))


@batch_transform
def calculate_theta(datapanel, sid, num):
    prices = datapanel['price'][sid]
    for i in range(len(prices)):
        if prices[i] is None:
            return None
    testX  = [[prices[i] for i in range(j, j + 4)] for j in range(0, 60, 5)]
    avg    = [np.average(testX[k]) for k in range(len(testX))]
    testY  = [np.sign(prices[5 * i + 4] - avg[i]) for i in range(len(testX))]
    theta  = hlsgdA(testX, testY, 0.01, randomIndex, num)
    priceh = prices[-4:]  # get historical data for the last four days
    return (theta, priceh)


# stochastic gradient descent using hinge loss function
def hlsgdA(X, Y, l, nextIndex, numberOfIterations):
    theta = np.zeros(len(X[0]))
    best  = np.zeros(len(X[0]))
    e = 0
    omega = 1.0 / (2 * len(Y))
    while e < numberOfIterations:
        ita = 1.0 / (1 + e)
        for i in range(len(Y)):
            index = nextIndex(len(Y))
            k = np.dot(ita, (np.dot(l, np.append([0], [k for k in theta[1:]])) -
                np.dot((sign(1 - Y[index] * np.dot(theta, X[index])) * Y[index]), X[index])))
            theta -= k
            # a recency-weighted average of theta: an average that exponentially decays the influence of older theta values
            best = (1 - omega) * best + omega * theta
        e += 1
    return best


# sign operations to identify mistakes
def sign(k):
    if k <= 0:
        return 0
    else:
        return 1


def randomIndex(n):
    return random.randint(0, n - 1)
