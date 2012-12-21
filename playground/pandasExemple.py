"""
Some examples playing around with yahoo finance data
"""

from datetime import datetime

import matplotlib.finance as fin
import numpy as np
from pylab import show


from pandas import Index, DataFrame
from pandas.core.datetools import BMonthEnd
from pandas import ols

startDate = datetime(2008, 1, 1)
endDate = datetime(2009, 9, 1)
print startDate

def getQuotes(symbol, start, end):
    quotes = fin.quotes_historical_yahoo(symbol, start, end)
    dates, open, close, high, low, volume = zip(*quotes)

    data = {
        'open' : open,
        'close' : close,
        'high' : high,
        'low' : low,
        'volume' : volume
    }

    dates = Index([datetime.fromordinal(int(d)) for d in dates])
    return DataFrame(data, index=dates)

msft = getQuotes('MSFT', startDate, endDate)
aapl = getQuotes('AAPL', startDate, endDate)
goog = getQuotes('GOOG', startDate, endDate)
ibm = getQuotes('IBM', startDate, endDate)

px = DataFrame({'MSFT' : msft['close'],
                'IBM' : ibm['close'],
                'GOOG' : goog['close'],
                'AAPL' : aapl['close']})

print px

returns = px / px.shift(1) - 1

# Select dates

subIndex = ibm.index[(ibm['close'] > 95) & (ibm['close'] < 100)]
msftOnSameDates = msft.reindex(subIndex)

# Insert columns

msft['hi-lo spread'] = msft['high'] - msft['low']
ibm['hi-lo spread'] = ibm['high'] - ibm['low']

# Aggregate monthly

def toMonthly(frame, how):
    offset = BMonthEnd()
    return frame.groupby(offset.rollforward).aggregate(how)

msftMonthly = toMonthly(msft, np.mean)
ibmMonthly = toMonthly(ibm, np.mean)
print 'toMonthly: ', ibmMonthly

# Statistics

stdev = DataFrame({
    'MSFT' : msft.std(),
    'IBM'  : ibm.std()
})
print 'stdev: ', stdev

# Arithmetic

ratios = ibm / msft
print 'Ratios: ', ratios

# Works with different indices

ratio = ibm / ibmMonthly
monthlyRatio = ratio.reindex(ibmMonthly.index)
print 'Monthly ratio: ', monthlyRatio

# Ratio relative to past month average

filledRatio = ibm / ibmMonthly.reindex(ibm.index, method='pad')
print 'Month average: ', filledRatio
