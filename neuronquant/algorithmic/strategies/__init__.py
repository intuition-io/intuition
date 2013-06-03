'''
Portfolio managers
'''

from followers import (
    BuyAndHold,
    FollowTrend,
    RegularRebalance
)
from movingaverage import (
    DualMovingAverage,
    Momentum,
    MovingAverageCrossover,
    VolumeWeightAveragePrice
)
from stddev import StddevBased
from machinelearning import StochasticGradientDescent
from patate import MarkovGenerator

from orderbased import AutoAdjustingStopLoss

__all__ = [
        'followers',
        'movingaverage',
        'stddev',
        'machinelearning',
        'patate',
        'orderbased'
        ]
