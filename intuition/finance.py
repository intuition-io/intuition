# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Intuition financial library
  ---------------------------

  :copyright (c) 2014 Xavier Bruhiere
  :license: Apache 2.0, see LICENSE for more details.
'''


from pandas.core.datetools import BDay
import numpy as np
import math
import datetime as dt


class DailyReturn(object):
    '''
    >>> returns = DailyReturn()
    >>> returns(1.34)
    0.0
    >>> returns(1.37)
    2.2388059701492558
    '''
    _last_price = None

    def __call__(self, new_price):
        if self._last_price:
            daily_return = ((new_price - self._last_price)
                            / self._last_price) * 100
        else:
            daily_return = 0.0

        self._last_price = new_price

        return daily_return


# NOTE This is temporary copied from QSTK library
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


def moving_average(data, periods, method='simple'):
    """
    compute a <periods> period moving average.
    method is 'simple' | 'exponential'
    """
    data = np.asarray(data)
    if method == 'simple':
        weights = np.ones(periods)
    else:
        weights = np.exp(np.linspace(-1., 0., periods))

    weights /= weights.sum()

    mavg = np.convolve(data, weights, mode='full')[:len(data)]
    mavg[:periods] = mavg[periods]
    return mavg


def relative_strength(prices, periods=14):
    """
    compute the <periods> period relative strength indicator
    http://stockcharts.com/school/doku.php?\
        id=chart_school:glossary_r#relativestrengthindex
    http://www.investopedia.com/terms/r/rsi.asp
    """
    deltas = np.diff(prices)
    seed = deltas[:periods + 1]
    up = seed[seed >= 0].sum() / periods
    down = -seed[seed < 0].sum() / periods
    ratio = up / down
    rsi = np.zeros_like(prices)
    rsi[:periods] = 100. - 100. / (1. + ratio)

    for i in range(periods, len(prices)):
        delta = deltas[i - 1]  # Cause the diff is 1 shorter

        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta

        up = (up * (periods - 1) + upval) / periods
        down = (down * (periods - 1) + downval) / periods

        ratio = up / down
        rsi[i] = 100. - 100. / (1. + ratio)

    return rsi


def moving_average_convergence(data, nslow=26, nfast=12):
    """
    compute the MACD (Moving Average Convergence/Divergence)
    using a fast and slow exponential moving avg
    return value is emaslow, emafast, macd which are len(data) arrays
    """
    emaslow = moving_average(data, nslow, method='exponential')
    emafast = moving_average(data, nfast, method='exponential')
    return emaslow, emafast, emafast - emaslow


def cc_annualize_returns(ret_per_period, periods_per_year):
    ''' Compute cumulative compound annualize returns '''
    return math.log(1 + annualized_returns(ret_per_period, periods_per_year))


def annualized_returns(ret_per_period, periods_per_year):
    ''' Could use:
    res1 = averageReturns(Series([ret_per_period]*periods_per_year), \
            period=1, method='net')
    '''
    return pow(1 + ret_per_period, periods_per_year) - 1


def average_returns(data, **kwargs):
    ''' Compute geometric average returns from a returns time serie'''
    average_type = kwargs.get('method', 'net')
    if average_type == 'net':
        relative = 0
    else:
        relative = -1  # gross
    #start = kwargs.get('start', data.index[0])
    #end = kwargs.get('end', data.index[len(data.index) - 1])
    #delta = kwargs.get('delta', data.index[1] - data.index[0])
    period = kwargs.get('period', None)
    if isinstance(period, int):
        pass
    #else:
        #data = reIndexDF(data, start=start, end=end, delta=delta)
        #period = 1
    avg_ret = 1
    for idx in range(len(data.index)):
        if idx % period == 0:
            avg_ret *= (1 + data[idx] + relative)
    return avg_ret - 1


def cc_returns(data, **kwargs):
    ''' Compute cumulative compound returns '''
    start = kwargs.get('start', None)
    end = kwargs.get('end', dt.datetime.today())
    delta = kwargs.get('deltaya', BDay())
    period = kwargs.get('period', None)
    rets = returns(data, method='net', start=start, end=end,
                   delta=delta, period=period)
    return math.log(1 + rets)


# TODO care of dividends
# TODO care of inflation
def returns(data, **kwargs):
    '''
    Compute returns on the given period

    @param data : time serie to process
    @param kwargs.method: gross or simple returns
    @param delta : period betweend two computed returns
    @param start : with end, will return the return betweend this elapsed time
    @param period : delta is the number of lines/periods provided
    @param end : so said
    @param cumulative: compute cumulative returns
    '''
    returns_type = kwargs.get('method', 'net')
    cumulative = kwargs.get('cumulative', False)
    if returns_type == 'net':
        relative = 0
    else:
        relative = 1  # gross
    start = kwargs.get('start', None)
    end = kwargs.get('end', dt.datetime.today())
    #delta = kwargs.get('delta', None)
    period = kwargs.get('period', 1)
    if isinstance(start, dt.datetime):
        return data[end] / data[start] - 1 + relative
    #elif isinstance(delta, pd.DateOffset) or isinstance(delta, dt.timedelta):
        # FIXME timezone problem
        # FIXME reIndexDF is deprecated
        #data = reIndexDF(data, delta=delta)
        #period = 1
    rets_df = data / data.shift(period) - 1 + relative
    if cumulative:
        return rets_df.cumprod()
    return rets_df[1:]


def daily_returns(data, **kwargs):
    ''' re-compute data on a daily basis '''
    relative = kwargs.get('relative', 0)
    return returns(data, delta=BDay(), relative=relative)


def sharpe_ratio(data):
    ''' Compute sharpe from portfolio historical values '''
    # TODO Dataframe handler
    rets = daily_returns(data)
    return (np.mean(rets) / rets.stdev()) * np.sqrt(len(rets))


def high_low_spread(data):
    ''' Compute continue spread on given dataframe every offset period '''
    # TODO: handling the offset period with reindexing or resampling, like:
    # subIndex = df.index[conditions]
    # df = df.reindex(subIndex)
    return data['high'] - data['low']
