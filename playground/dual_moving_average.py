import sys, os

import matplotlib.pyplot as plt

from zipline.algorithm import TradingAlgorithm
from zipline.transforms import MovingAverage
from zipline.utils.factory import load_from_yahoo

sys.path.append(str(os.environ['QTRADE']))
from pyTrade.data.DataAgent import DataAgent
import pytz
import pandas as pd

class DualMovingAverage(TradingAlgorithm):
    """Dual Moving Average Crossover algorithm.

    This algorithm buys apple once its short moving average crosses
    its long moving average (indicating upwards momentum) and sells
    its shares once the averages cross again (indicating downwards
    momentum).

    """
    def initialize(self, short_window=200, long_window=400, amount=100000):
        self.amount = amount
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


if __name__ == '__main__':
    #data = load_from_yahoo(stocks=['AAPL'], indexes={})
    # data is a pandas dataframe, with daily freq from 1993-01-04 to 2001-12-31
    # and one column corresponding to stocks
    #-------------------------------------------------- My try -------
    dataobj = DataAgent('stocks.db')
    start = pd.datetime(2008,6,20, 0, 0, 0, 0, pytz.utc)
    end = pd.datetime(2010,4,1, 0, 0, 0, 0, pytz.utc)
    delta = pd.datetools.timedelta(days=1)
    data_tmp = dataobj.getQuotes(['altair'], ['open'], \
            start=start, end=end, delta=delta, reverse=True)
    data = data_tmp['open']
    #data.index = data.index.tz_localize(pytz.utc)
    #-----------------------------------------------------------------
    print data.head()
    print('\n-- Running backetester\n')
    dma = DualMovingAverage(50, 100, 50000)
    results = dma.run(data, start, end)

    results.portfolio_value.plot()
    #results.returns.plot()
    #print('--------------------------------------------    Results   ----\n{}'.format(results.head()))

    data['short'] = dma.short_mavgs
    data['long'] = dma.long_mavgs
    data[['altair', 'short', 'long']].plot()
    plt.legend(loc=0)
    plt.show()
