'''
Portfolio managers
'''

from followers import BuyAndHold, FollowTrend
from movingaverage import (
        DualMovingAverage,
        Momentum,
        MovingAverageCrossover,
        MultiMA,
        VolumeWeightAveragePrice
)
from olmar import OLMAR
from pairtrade import Pairtrade
from stddev import StddevBased
from bollingerbands import BollingerBands
from machinelearning import (
        PredictHiddenStates,
        StochasticGradientDescent
)
from orderbased import AutoAdjustingStopLoss

__all__ = [
        'followers',
        'movingaverage',
        'pairtrade',
        'stddev',
        'olmar',
        'machinelearning',
        'orderbased'
        ]
