#
# Copyright 2012 Xavier Bruhiere
#
# Licensed under the Apache License, Version 2.0 (the License);
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an AS IS BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# !!
# This file has been automatically generated
# Don't edit it manually, use update_library.sh script instead
# !!


import logbook
log = logbook.Logger('Library')


from neuronquant.algorithmic.strategies.followers import BuyAndHold,FollowTrend,RegularRebalance
from neuronquant.algorithmic.strategies.machinelearning import StochasticGradientDescent
from neuronquant.algorithmic.strategies.movingaverage import DualMovingAverage,VolumeWeightAveragePrice,Momentum,MovingAverageCrossover
from neuronquant.algorithmic.strategies.orderbased import AutoAdjustingStopLoss
from neuronquant.algorithmic.strategies.patate import MarkovGenerator
from neuronquant.algorithmic.strategies.stddev import StddevBased
from neuronquant.algorithmic.managers.constant import Constant
from neuronquant.algorithmic.managers.fair import Fair
from neuronquant.algorithmic.managers.gmv import GlobalMinimumVariance
from neuronquant.algorithmic.managers.optimalfrontier import OptimalFrontier
from neuronquant.data.ziplinesources.backtest.csv import CSVSource
from neuronquant.data.ziplinesources.backtest.database import DBPriceSource
from neuronquant.data.ziplinesources.backtest.quandl import QuandlSource
from neuronquant.data.ziplinesources.backtest.yahoostock import YahooPriceSource,YahooOHLCSource
from neuronquant.data.ziplinesources.live.equities import EquitiesLiveSource
from neuronquant.data.ziplinesources.live.forex import ForexLiveSource


algorithms = {'BuyAndHold': BuyAndHold,'FollowTrend': FollowTrend,'RegularRebalance': RegularRebalance,'StochasticGradientDescent': StochasticGradientDescent,'DualMovingAverage': DualMovingAverage,'VolumeWeightAveragePrice': VolumeWeightAveragePrice,'Momentum': Momentum,'MovingAverageCrossover': MovingAverageCrossover,'AutoAdjustingStopLoss': AutoAdjustingStopLoss,'MarkovGenerator': MarkovGenerator,'StddevBased': StddevBased,}

portfolio_managers = {'Constant': Constant,'Fair': Fair,'GlobalMinimumVariance': GlobalMinimumVariance,'OptimalFrontier': OptimalFrontier,}

data_sources = {'CSVSource': CSVSource,'DBPriceSource': DBPriceSource,'QuandlSource': QuandlSource,'YahooPriceSource': YahooPriceSource,'YahooOHLCSource': YahooOHLCSource,'EquitiesLiveSource': EquitiesLiveSource,'ForexLiveSource': ForexLiveSource,}


#TODO optimization algos

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
