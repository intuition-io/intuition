''' 
Coursera, Introduction to computational Finance and Financial econometrics
Assignment 1 - Computations
'''

import sys, os
sys.path.append(str(os.environ['QTRADE']))
from pyTrade.data.DataAgent import DataAgent
from pyTrade.utils.LogSubsystem import LogSubsystem
from pyTrade.data.QuantDB import Fields
from pyTrade.compute.QuantSubsystem import Quantitative
from pyTrade.compute.Algorithms import Backtester 

from pandas.core.datetools import BMonthEnd
from pandas import date_range, Series
import datetime as dt
import matplotlib.pyplot as plt

import pytz

'''-------------------------------------- Notes
Zipline uses a benchmark data very interesting (see utils/factory.py and data/benchmark.py)
Modifying it to take in parameter an action and to process associated market ? only s&p500 at the moment
'''

if __name__ == '__main__':
    ''' -----------------------------------------------------------------    Data   -----'''
    # Thiz tzinfo is annoying ! default to provide if forgotten, or the one sent 
    #through the init of dataagent. See also zipline.loader_utils.py
    timestamp = date_range(dt.datetime(2004,12,31, tzinfo=pytz.utc), \
            dt.datetime(2005,12,31, tzinfo=pytz.utc), freq='M')
    ticker = 'starbucks'

    #TODO implement a how method wich give the same results as in table
    #put in some DataAgent properties ?
    db_agent = DataAgent('stocks.db')
    data = db_agent.getQuotes([ticker], ['adj_close'], index=timestamp, \
            save=True, reverse=True)
    #ts = Series(data[ticker]['adj_close'], name=ticker)
    ts = data['adj_close'][ticker]

    #ts = Series([31.18, 27.0, 25.91, 25.83, 24.76, 27.4, 25.83, 26.27, \
            #24.51, 25.05, 28.28, 30.45, 30.51], index=timestamp)
    ''' ----------------------------------------------------------------------------------'''

    print
    print('-'*60)
    #1 Simple monthly return between the end of December 2004 and the end of January 2005
    compute = Quantitative(lvl='error')
    monthly_ret = compute.returns(ts, start=dt.datetime(2004,12,31), end=dt.datetime(2005,1,31))
    print('1. Return = {} %'.format(monthly_ret*100.0))
    
    #2 $10,000 of starbucks in December 2004, how much in 2005 ?
    print('2. Portfolio value at the end of january: {}'.format(10000*(1+monthly_ret)))

    #3 Continously compounded monthly return  beween December 2004 and January 2005
    cc_monthly_ret = compute.CCReturns(ts, start=dt.datetime(2004,12,31), \
            end=dt.datetime(2005,1,31))
    print('3. CC Return = {} %'.format(cc_monthly_ret*100.0))

    #4 Annual return with monthly compounded
    annual_rate = compute.annualizedReturns(monthly_ret, 12)
    print('4. Annual constant simple rate: {} %'.format(annual_rate*100.0))

    #5 Annual continuously compounded return
    cc_annual_rate = compute.CCAnnualizedReturns(monthly_ret, 12)
    print('5. Annual constant continuously compounded simple rate: {} %'.format(cc_annual_rate*100.0))

    #6 Simple annual return between decembers 2004 and 2005
    annual_ret = compute.returns(ts, start=dt.datetime(2004,12,31), end=dt.datetime(2005,12,30))
    print('6. Annual simple return: {}'.format(annual_ret*100.0))

    #7 How much earned on this period with $10 000 invested
    print('7. Earned on this period with 10,000 invested: {}'.format(10000*(1+annual_ret)))

    
    #6 Continuously compounded annual return between decembers 2004 and 2005
    cc_monthly_ret = compute.CCReturns(ts, start=dt.datetime(2004,12,31), \
            end=dt.datetime(2005,12,30))
    print('8. CC Return = {} %'.format(cc_monthly_ret*100.0))
    print('-'*60)
    print

    db_agent._db.close(commit=True)
