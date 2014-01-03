#
# Copyright 2013 Xavier Bruhiere
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import logbook
from pandas.core.datetools import BDay
import numpy as np
import math
import datetime as dt

#from intuition.utils.utils import reIndexDF


'''-----------------------------------------------------------
Quant
-----------------------------------------------------------'''

log = logbook.Logger('intuition.core.finance')


#NOTE This is temporary copied from QSTK library
#     which will be more used in the future
def qstk_get_sharpe_ratio(rets, risk_free=0.00):
    """
    @summary Returns the daily Sharpe ratio of the returns.
    @param rets: 1d numpy array or fund list of daily returns (centered on 0)
    @param risk_free: risk free returns, default is 0%
    @return Annualized rate of return, not converted to percent
    """
    f_dev = np.std(rets, axis=0)
    f_mean = np.mean(rets, axis=0)

    f_sharpe = (f_mean * 252 - risk_free) / (f_dev * np.sqrt(252))

    return f_sharpe


def moving_average(x, n, type='simple'):
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


def relative_strength(prices, n=14):
    """
    compute the n period relative strength indicator
    http://stockcharts.com/school/doku.php?\
        id=chart_school:glossary_r#relativestrengthindex
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


def moving_average_convergence(x, nslow=26, nfast=12):
    """
    compute the MACD (Moving Average Convergence/Divergence)
    using a fast and slow exponential moving avg
    return value is emaslow, emafast, macd which are len(x) arrays
    """
    emaslow = moving_average(x, nslow, type='exponential')
    emafast = moving_average(x, nfast, type='exponential')
    return emaslow, emafast, emafast - emaslow


def CC_annualize_returns(ret_per_period, periods_per_year):
    return math.log(1 + annualized_returns(ret_per_period, periods_per_year))


def annualized_returns(ret_per_period, periods_per_year):
    ''' Could use:
    res1 = averageReturns(Series([ret_per_period]*periods_per_year), \
            period=1, type='net')
    '''
    return pow(1 + ret_per_period, periods_per_year) - 1


def average_returns(ts, **kwargs):
    ''' Compute geometric average returns from a returns time serie'''
    type = kwargs.get('type', 'net')
    if type == 'net':
        relative = 0
    else:
        relative = -1  # gross
    #start = kwargs.get('start', ts.index[0])
    #end = kwargs.get('end', ts.index[len(ts.index) - 1])
    #delta = kwargs.get('delta', ts.index[1] - ts.index[0])
    period = kwargs.get('period', None)
    if isinstance(period, int):
        pass
    #else:
        #FIXME reIndexDF is deprecated
        #ts = reIndexDF(ts, start=start, end=end, delta=delta)
        #period = 1
    avg_ret = 1
    for idx in range(len(ts.index)):
        if idx % period == 0:
            avg_ret *= (1 + ts[idx] + relative)
    return avg_ret - 1


def CC_returns(ts, **kwargs):
    start = kwargs.get('start', None)
    end = kwargs.get('end', dt.datetime.today())
    delta = kwargs.get('deltaya', BDay())
    period = kwargs.get('period', None)
    rets = returns(ts, type='net', start=start, end=end,
                   delta=delta, period=period)
    return math.log(1 + rets)


#TODO care of dividends
#TODO care of inflation
def returns(ts, **kwargs):
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
    #delta = kwargs.get('delta', None)
    period = kwargs.get('period', 1)
    if isinstance(start, dt.datetime):
        log.debug('{} / {} -1'.format(ts[end], ts[start]))
        return ts[end] / ts[start] - 1 + relative
    #elif isinstance(delta, pd.DateOffset) or isinstance(delta, dt.timedelta):
        #FIXME timezone problem
        #FIXME reIndexDF is deprecated
        #ts = reIndexDF(ts, delta=delta)
        #period = 1
    rets_df = ts / ts.shift(period) - 1 + relative
    if cumulative:
        return rets_df.cumprod()
    return rets_df[1:]


def daily_returns(ts, **kwargs):
    relative = kwargs.get('relative', 0)
    return returns(ts, delta=BDay(), relative=relative)


def panel_to_retsDF(dataPanel, kept_field='close', type='dataframe'):
    '''
    @summary transform data in DataAccess format to a dataframe
             suitable for qstk.tsutils.optimizePortfolio()
    @param dataPanel: data like quotes['close']['google']
    @output : a dataframe, cols = companies, rows = dates
    '''
    #TODO Here a need of data normalisation
    df = dataPanel[kept_field]
    df.fillna(method='ffill')
    df.fillna(method='backfill')
    if type == 'array':
        return returns(df, relative=0).values
    return returns(df, relative=0)  # 1 in doc, 0 in example


def sharpe_ratio(ts):
    #TODO: Dataframe handler
    rets = daily_returns(ts)
    return (np.mean(rets) / rets.stdev()) * np.sqrt(len(rets))


def high_low_spread(df, offset):
    ''' Compute continue spread on given datafrme every offset period '''
    #TODO: handling the offset period with reindexing or resampling, sthg like:
    # subIndex = df.index[conditions]
    # df = df.reindex(subIndex)
    return df['high'] - df['low']
