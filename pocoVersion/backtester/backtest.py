import sys, os

import matplotlib.pyplot as plt

sys.path.append(str(os.environ['QTRADE']))
from pyTrade.data.DataAgent import DataAgent
from pyTrade.algos.DualMovingAverage import DualMovingAverage
import pytz
import pandas as pd

class Backtester(object):
    ''' Factory class wrapping zipline Backtester, returns the requested algo '''
    algos = {'dualMA': DualMovingAverage} 

    def __new__(self, algo, **kwargs):
        if not Backtester.algos[algo]:
            raise NotImplementedError('Algorithm {} not available or implemented'.format(algo))
        print kwargs
        return Backtester.algos[algo](kwargs)



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
    #dma = DualMovingAverage(50, 100, 50000)
    strategie = Backtester('dualMA', short_window=50, long_window=100, amount=50000)
    results = strategie.run(data, start, end)

    results.portfolio_value.plot()
    #results.returns.plot()
    #print('--------------------------------------------    Results   ----\n{}'.format(results.head()))

    data['short'] = strategie.short_mavgs
    data['long'] = strategie.long_mavgs
    data[['altair', 'short', 'long']].plot()
    plt.legend(loc=0)
    plt.show()
