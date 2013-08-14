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
def HMM(data, sid, means_prior=None):
    # data is _not_ an event-frame, but an array
    # of the most recent trade events

    # Create scikit-learn model using the means
    # from the previous model as a prior
    model = GaussianHMM(HIDDEN_STATES,
                        covariance_type="diag",
                        n_iter=10,
                        means_prior=means_prior,
                        means_weight=0.5)

    # Extract variation and volume
    diff = data.variation[sid].values
    volume = data.volume[sid].values
    X = np.column_stack([diff, volume])

    if len(diff) < HIDDEN_STATES:
        return None

    # Estimate model
    model.fit([X])

    return model


class PredictHiddenStates(TradingAlgorithm):
    def initialize(self, properties):
        # Instantiate batch_transform
        self.hmm_transform = HMM(refresh_period=properties.get('refresh_period', 100),  # recompute every 500 days
                                 window_length=properties.get('window_length', 300),
                                 compute_only_full=False)  # do not wait until window is full

        # State variables
        self.state = -1
        self.means_prior = None

        self.memory = {}

    def handle_data(self, data):
        if not self.initialized:
            self.initialized = True
            for sid in data:
                data[sid]['variation'] = 0.0
            return

        for sid in data:
            #data[sid]['variation'] = (data[sid].close_price - data[sid].open_price)
            data[sid]['variation'] = 0.0

            # Pass event frame to batch_transform
            # Will _not_ directly call the transform but append
            # data to a window until full and then compute.
            self.hmm = self.hmm_transform.handle_data(data, sid, means_prior=self.means_prior)

            # Have we fit the model yet?
            if self.hmm is None:
                return

            # Remember mean for the prior
            self.means_prior = self.hmm.means_

            # Predict current state
            data_vec = [data[sid].variation, data[sid].volume]
            self.state = self.hmm.predict([data_vec])
            self.record(state=self.state)

            self.logger.info(self.state)
