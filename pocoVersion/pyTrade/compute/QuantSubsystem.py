#!/usr/bin/python
# -*- coding: utf8 -*-

import sys

# Logger class (obviously...)
sys.path.append('..')
from data.QuantDB import QuantSQLite
from utils.LogSubsystem import LogSubsystem

# For mathematical stuff, data manipulation...
from pandas import Index, DataFrame
# Statsmodels has ols too, benchamark needed
#from pandas import ols

import numpy as np


'''---------------------------------------------------------------------------------------
Quant
---------------------------------------------------------------------------------------'''
class Quantitative:
    ''' Trade qunatitativ module 
    an instanciation work on a data set specified while initializing'''
    def __init__(self, logger=None):
        if logger == None:
            self._logger = LogSubsystem('Computer', "debug").getLog()
        else:
            self._logger = logger

    def movingAverage(self, x, n, type='simple'):
        """
        compute an n period moving average.
        type is 'simple' | 'exponential'
        """
        x = np.asarray(x)
        if type=='simple':
            weights = np.ones(n)
        else:
            weights = np.exp(np.linspace(-1., 0., n))

        weights /= weights.sum()


        a =  np.convolve(x, weights, mode='full')[:len(x)]
        a[:n] = a[n]
        return a

    def relativeStrength(self, prices, n=14):
        """
        compute the n period relative strength indicator
        http://stockcharts.com/school/doku.php?id=chart_school:glossary_r#relativestrengthindex
        http://www.investopedia.com/terms/r/rsi.asp
        """
        deltas = np.diff(prices)
        seed = deltas[:n+1]
        up = seed[seed>=0].sum()/n
        down = -seed[seed<0].sum()/n
        rs = up/down
        rsi = np.zeros_like(prices)
        rsi[:n] = 100. - 100./(1.+rs)

        for i in range(n, len(prices)):
            delta = deltas[i-1] # cause the diff is 1 shorter

            if delta>0:
                upval = delta
                downval = 0.
            else:
                upval = 0.
                downval = -delta

            up = (up*(n-1) + upval)/n
            down = (down*(n-1) + downval)/n

            rs = up/down
            rsi[i] = 100. - 100./(1.+rs)

        return rsi

    def movingAverageConvergence(self, x, nslow=26, nfast=12):
        """
        compute the MACD (Moving Average Convergence/Divergence) using a fast and slow exponential moving avg'
        return value is emaslow, emafast, macd which are len(x) arrays
        """
        emaslow = self.movingAverage(x, nslow, type='exponential')
        emafast = self.movingAverage(x, nfast, type='exponential')
        return emaslow, emafast, emafast - emaslow

    def returns(self, ts, period, relative=0):
        ''' Compute returns on the given period '''
        #TODO: freq parameter etc...
        return ts / ts.shift(period) - 1 + relative

    def dailyReturns(self, ts, relative=0):
        #TODO: smart index date handler
        return self.returns(ts, 1, relative)

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

