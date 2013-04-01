'''
Portfolio managers
'''

from buyandhold import BuyAndHold
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

__all__ = [
        'buyandhold',
        'movingaverage',
        'pairtrade',
        'stddev',
        'olmar'
        ]
