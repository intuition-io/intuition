import sys
import os

# Logger class (obviously...)
sys.path.append(str(os.environ['QTRADE']))
from pyTrade.utils.LogSubsystem import LogSubsystem
from pyTrade.utils.utils import reIndexDF

# For mathematical stuff, data manipulation...
import pandas as pd
from pandas.core.datetools import BDay
# Statsmodels has ols too, benchamark needed
#from pandas import ols

import numpy as np
import math
import datetime as dt


'''---------------------------------------------------------------------------------------
Quant
---------------------------------------------------------------------------------------'''


class Quantitative(object):
    ''' Trade qunatitativ modul '''
    def __init__(self, logger=None, lvl='debug'):
        if logger is None:
            self._logger = LogSubsystem('Computer', lvl).getLog()
        else:
            self._logger = logger

    def movingAverage(self, x, n, type='simple'):
        """
        compute an n period moving average.
        type is 'simple' | 'exponential'
        """
        x = np.asarray(x)
        if type == 'simple':
            weights = np.ones(n)
        else:
            weights = np.exp(np.linspace(-1., 0., n))

        weights /= weights.sum()

        a = np.convolve(x, weights, mode='full')[:len(x)]
        a[:n] = a[n]
        return a

    def relativeStrength(self, prices, n=14):
        """
        compute the n period relative strength indicator
        http://stockcharts.com/school/doku.php?id=chart_school:glossary_r#relativestrengthindex
        http://www.investopedia.com/terms/r/rsi.asp
        """
        deltas = np.diff(prices)
        seed = deltas[:n + 1]
        up = seed[seed >= 0].sum() / n
        down = -seed[seed < 0].sum() / n
        rs = up / down
        rsi = np.zeros_like(prices)
        rsi[:n] = 100. - 100. / (1. + rs)

        for i in range(n, len(prices)):
            delta = deltas[i - 1]  # Cause the diff is 1 shorter

            if delta > 0:
                upval = delta
                downval = 0.
            else:
                upval = 0.
                downval = -delta

            up = (up * (n - 1) + upval) / n
            down = (down * (n - 1) + downval) / n

            rs = up / down
            rsi[i] = 100. - 100. / (1. + rs)

        return rsi

    def movingAverageConvergence(self, x, nslow=26, nfast=12):
        """
        compute the MACD (Moving Average Convergence/Divergence) using a fast and slow exponential moving avg'
        return value is emaslow, emafast, macd which are len(x) arrays
        """
        emaslow = self.movingAverage(x, nslow, type='exponential')
        emafast = self.movingAverage(x, nfast, type='exponential')
        return emaslow, emafast, emafast - emaslow

    def CCAnnualizedReturns(self, ret_per_period, periods_per_year):
        return math.log(1 + self.annualizedReturns(ret_per_period, periods_per_year))

    def annualizedReturns(self, ret_per_period, periods_per_year):
        ''' Could use:
        res1 = self.averageReturns(Series([ret_per_period]*periods_per_year), \
                period=1, type='net')
        '''
        return pow(1 + ret_per_period, periods_per_year) - 1

    def averageReturns(self, ts, **kwargs):
        ''' Compute geometric average returns from a returns time serie'''
        type = kwargs.get('type', 'net')
        if type == 'net':
            relative = 0
        else:
            relative = -1  # gross
        start = kwargs.get('start', ts.index[0])
        end = kwargs.get('end', ts.index[len(ts.index) - 1])
        delta = kwargs.get('delta', ts.index[1] - ts.index[0])
        period = kwargs.get('period', None)
        if isinstance(period, int):
            pass
        else:
            ts = reIndexDF(ts, start=start, end=end, delta=delta)
            period = 1
        avg_ret = 1
        for idx in range(len(ts.index)):
            if idx % period == 0:
                avg_ret *= (1 + ts[idx] + relative)
        return avg_ret - 1

    def CCReturns(self, ts, **kwargs):
        start = kwargs.get('start', None)
        end = kwargs.get('end', dt.datetime.today())
        delta = kwargs.get('deltaya', BDay())
        period = kwargs.get('period', None)
        rets = self.returns(ts, type='net', start=start, end=end, delta=delta, period=period)
        return math.log(1 + rets)

    #TODO dividends in account
    #TODO inflation in account
    def returns(self, ts, **kwargs):
        '''
        Compute returns on the given period
        @param ts : time serie to process
        @param kwargs.type: gross or simple returns
        @param delta : period betweend two computed returns
        @param start : with end, will return the return betweend this elapsed time
        @param period : delta is the number of lines/periods provided
        @param end : so said
        @param cumulative: compute cumulative returns
        '''
        type = kwargs.get('type', 'net')
        cumulative = kwargs.get('cumulative', False)
        if type == 'net':
            relative = 0
        else:
            relative = 1  # gross
        start = kwargs.get('start', None)
        end = kwargs.get('end', dt.datetime.today())
        delta = kwargs.get('delta', None)
        period = kwargs.get('period', 1)
        if isinstance(start, dt.datetime):
            self._logger.debug('{} / {} -1'.format(ts[end], ts[start]))
            return ts[end] / ts[start] - 1 + relative
        elif isinstance(delta, pd.DateOffset) or isinstance(delta, dt.timedelta):
            #FIXME timezone problem
            ts = reIndexDF(ts, delta=delta)
            period = 1
        rets_df = ts / ts.shift(period) - 1 + relative
        if cumulative:
            return rets_df.cumprod()
        return rets_df[1:]

    def dailyReturns(self, ts, **kwargs):
        relative = kwargs.get('relative', 0)
        return self.returns(ts, delta=BDay(), relative=relative)

    def panelToRetsDF(self, dataPanel, kept_field='close', type='dataframe'):
        '''
        @summary transform data in DataAccess format to a dataframe suitable for qstk.tsutils.optimizePortfolio()
        @param dataPanel get with the reverse flag: data like quotes['close']['google']
        @output : a dataframe, cols = companies, rows = dates
        '''
        #TODO Here a need of data normalisation
        df = dataPanel[kept_field]
        df.fillna(method='ffill')
        df.fillna(method='backfill')
        if type == 'array':
            return self.returns(df, relative=0).values
        return self.returns(df, relative=0)  # 1 in doc, 0 in example

    def sharpeRatio(self, ts):
        #TODO: Dataframe handler
        rets = self.dailyReturns(ts)
        return (np.mean(rets) / rets.stdev()) * np.sqrt(len(rets))

    def HighLowSpread(self, df, offset):
        ''' Compute continue spread on given datafrme every offset period '''
        #TODO: handling the offset period with reindexing or resampling, sthg like:
        # subIndex = df.index[conditions]
        # df = df.reindex(subIndex)
        return df['high'] - df['low']

  #TODO: updateDB, every class has this method, factorisation ? shared memory map to synchronize

'''---------------------------------------------------------------------------------------
Usage Exemple
---------------------------------------------------------------------------------------'''
'''
if __name__ == '__main__':
'''
