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


import logbook
log = logbook.Logger('Library')

#TODO test with *
from neuronquant.algorithmic.strategies import (
    StddevBased,
    DualMovingAverage,
    Momentum,
    RegularRebalance,
    VolumeWeightAveragePrice,
    BuyAndHold,
    MovingAverageCrossover,
    AutoAdjustingStopLoss,
    FollowTrend,
    MarkovGenerator,
    StochasticGradientDescent
)

from neuronquant.algorithmic.managers import (
    Constant,
    Fair,
    GlobalMinimumVariance,
    OptimalFrontier
)

from neuronquant.data.ziplinesources import (
    YahooPriceSource,
    YahooOHLCSource,
    QuandlSource,
    ForexLiveSource,
    CSVSource,
    DBPriceSource,
    EquitiesLiveSource
)


algorithms = {'DualMA'  : DualMovingAverage       , 'Momentum'   : Momentum,
              'VWAP'    : VolumeWeightAveragePrice, 'BuyAndHold' : BuyAndHold,
              'StdBased': StddevBased             , 'MACrossover': MovingAverageCrossover,
              'Follower': FollowTrend             , 'Gradient'   : StochasticGradientDescent,
              'AASL'    : AutoAdjustingStopLoss   , 'Rebalance'  : RegularRebalance,
              'Markov'  : MarkovGenerator}


portfolio_managers = {'Fair': Fair, 'Constant': Constant, 'OptimalFrontier': OptimalFrontier,
                      'GMV' : GlobalMinimumVariance}


data_sources = {'forex_live': ForexLiveSource, 'equities_live': EquitiesLiveSource,
                'quandl'    : QuandlSource,    'default'      : YahooPriceSource,
                'yahooOHLC' : YahooOHLCSource, 'csv'          : CSVSource,
                'database'  : DBPriceSource}


def check_availability(algo, manager, source):
    if algo not in algorithms:
        raise NotImplementedError('Algorithm {} not available or implemented'.format(algo))
    log.debug('Algorithm {} available, getting a reference on it.'.format(algo))

    if (manager) and (manager not in portfolio_managers):
        raise NotImplementedError('Manager {} not available or implemented'.format(manager))
    log.debug('Manager {} available, getting a reference on it.'.format(manager))

    if (source) and (source not in data_sources):
        raise NotImplementedError('Source {} not available or implemented'.format(source))
    log.debug('Source {} available'.format(source))

    return True
