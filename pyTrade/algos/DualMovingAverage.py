import sys, os

import matplotlib.pyplot as plt

from zipline.algorithm import TradingAlgorithm
from zipline.transforms import MovingAverage
from zipline.utils.factory import load_from_yahoo

class DualMovingAverage(TradingAlgorithm):
    """Dual Moving Average Crossover algorithm.

    This algorithm buys apple once its short moving average crosses
    its long moving average (indicating upwards momentum) and sells
    its shares once the averages cross again (indicating downwards
    momentum).

    """
    #def initialize(self, short_window=200, long_window=400, amount=100000):
    def initialize(self, properties):
        short_window = properties.get('short_window', 200)
        long_window = properties.get('long_window', 400)
        self.amount = properties.get('amount', 10000)

        print('Short: {}, long: {}, amount: {}'.format(short_window, long_window, self.amount))

        # Add 2 mavg transforms, one with a long window, one
        # with a short window.
        # Add a field in stock object: (function to apply, key in stock dict, keys in previous dict, parameters)
        self.add_transform(MovingAverage, 'short_mavg', ['price'],
                           window_length=short_window)

        self.add_transform(MovingAverage, 'long_mavg', ['price'],
                           window_length=long_window)

        # To keep track of whether we invested in the stock or not
        self.invested = False

        self.short_mavgs = []
        self.long_mavgs = []

    def handle_data(self, data):
        short_mavg = data['altair'].short_mavg['price']
        long_mavg = data['altair'].long_mavg['price']
        if short_mavg > long_mavg and not self.invested:
            self.order('altair', 100)
            self.invested = True
        elif short_mavg < long_mavg and self.invested:
            self.order('altair', -100)
            self.invested = False

        # Save mavgs for later analysis.
        self.short_mavgs.append(short_mavg)
        self.long_mavgs.append(long_mavg)

