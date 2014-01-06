""" yahoofinance

This module provides a Python API for retrieving stock data from Yahoo Finance.

sample usage:
>>> import yahoofinance
>>> print yahoofinance.get_price('GOOG')
529.46
"""


import urllib
from bs4 import BeautifulSoup


def __request(symbol, stat):
    ''' Yahoo request factory method '''
    url = 'http://finance.yahoo.com/d/quotes.csv?s=%s&f=%s' % (symbol, stat)
    return urllib.urlopen(url).read().strip().strip('"')


def get_all(symbol):
    """
    Get all available quote data for the given ticker symbol.

    Returns a dictionary.
    """
    values = __request(symbol, 'l1c1va2xj1b4j4dyekjm3m4rr5p5p6s7').split(',')
    data = {}
    data['price'] = values[0]
    data['change'] = values[1]
    data['volume'] = values[2]
    data['avg_daily_volume'] = values[3]
    data['stock_exchange'] = values[4]
    data['market_cap'] = values[5]
    data['book_value'] = values[6]
    data['ebitda'] = values[7]
    data['dividend_per_share'] = values[8]
    data['dividend_yield'] = values[9]
    data['earnings_per_share'] = values[10]
    data['52_week_high'] = values[11]
    data['52_week_low'] = values[12]
    data['50day_moving_avg'] = values[13]
    data['200day_moving_avg'] = values[14]
    data['price_earnings_ratio'] = values[15]
    data['price_earnings_growth_ratio'] = values[16]
    data['price_sales_ratio'] = values[17]
    data['price_book_ratio'] = values[18]
    data['short_ratio'] = values[19]
    return data


def get_price(symbol):
    return __request(symbol, 'l1')


def get_change(symbol):
    return __request(symbol, 'c1')


def get_volume(symbol):
    return __request(symbol, 'v')


def get_avg_daily_volume(symbol):
    return __request(symbol, 'a2')


def get_stock_exchange(symbol):
    name = __request(symbol, 'x')
    if name == 'NasdaqNM':
        name = 'NASDAQ'
    return name


def get_market_cap(symbol):
    return __request(symbol, 'j1')


def get_book_value(symbol):
    return __request(symbol, 'b4')


def get_ebitda(symbol):
    return __request(symbol, 'j4')


def get_dividend_per_share(symbol):
    return __request(symbol, 'd')


def get_dividend_yield(symbol):
    return __request(symbol, 'y')


def get_earnings_per_share(symbol):
    return __request(symbol, 'e')


def get_52_week_high(symbol):
    return __request(symbol, 'k')


def get_52_week_low(symbol):
    return __request(symbol, 'j')


def get_50day_moving_avg(symbol):
    return __request(symbol, 'm3')


def get_200day_moving_avg(symbol):
    return __request(symbol, 'm4')


def get_price_earnings_ratio(symbol):
    return __request(symbol, 'r')


def get_price_earnings_growth_ratio(symbol):
    return __request(symbol, 'r5')


def get_price_sales_ratio(symbol):
    return __request(symbol, 'p5')


def get_price_book_ratio(symbol):
    return __request(symbol, 'p6')


def get_short_ratio(symbol):
    return __request(symbol, 's7')


def get_name(symbol):
    return __request(symbol, 'n')


def get_sector(symbol):
    '''
    Uses BeautifulSoup to scrape stock sector from Yahoo! Finance website
    '''
    url = 'http://finance.yahoo.com/q/pr?s=%s+Profile' % symbol
    soup = BeautifulSoup(urllib.urlopen(url).read())
    try:
        sector = soup.find('td', text='Sector:').\
            find_next_sibling().string.encode('utf-8')
    except:
        sector = ''
    return sector


def get_industry(symbol):
    '''
    Uses BeautifulSoup to scrape stock industry from Yahoo! Finance website
    '''
    url = 'http://finance.yahoo.com/q/pr?s=%s+Profile' % symbol
    soup = BeautifulSoup(urllib.urlopen(url).read())
    try:
        industry = soup.find('td', text='Industry:').\
            find_next_sibling().string.encode('utf-8')
    except:
        industry = ''
    return industry


def get_type(symbol):
    '''
    Uses BeautifulSoup to scrape symbol category from Yahoo! Finance website
    '''
    url = 'http://finance.yahoo.com/q/pr?s=%s+Profile' % symbol
    soup = BeautifulSoup(urllib.urlopen(url).read())
    if soup.find('span', text='Business Summary'):
        return 'Stock'
    elif soup.find('span', text='Fund Summary'):
        asset_type = 'Fund'
    elif symbol.find('^') == 0:
        asset_type = 'Index'
    else:
        pass
    return asset_type


def get_indices(symbol):
    url = 'http://finance.yahoo.com/q/pr?s=%s+Profile' % symbol
    soup = BeautifulSoup(urllib.urlopen(url).read())
    indices = []
    try:
        tmp_idx = soup.find('td', text='Index Membership:').\
            find_next_sibling().findAll('a')
        for idx in tmp_idx:
            indices.append(idx.text)
    except:
        pass
    return ','.join(indices)


def get_historical_prices(symbol, start_date, end_date):
    """
    Get historical prices for the given ticker symbol.
    Dates may either be a date object or a string with the following format:
    'YYYYMMDD'

    Returns a nested list.
    """
    if isinstance(start_date, str):
        # Months are zero-based
        start_m = str(int(start_date[4:6]) - 1)
        start_d = str(int(start_date[6:8]))
        start_y = str(int(start_date[0:4]))
    else:
        # Months are zero-based
        start_m = str(start_date.month - 1)
        start_d = str(start_date.day)
        start_y = str(start_date.year)

    if isinstance(end_date, str):
        # Months are zero-based
        end_m = str(int(end_date[4:6]) - 1)
        end_d = str(int(end_date[6:8]))
        end_y = str(int(end_date[0:4]))
    else:
        # Months are zero-based
        end_m = str(end_date.month - 1)
        end_d = str(end_date.day)
        end_y = str(end_date.year)

    url = 'http://ichart.yahoo.com/table.csv?s=%s&' % symbol + \
          'd=%s&' % end_m + \
          'e=%s&' % end_d + \
          'f=%s&' % end_y + \
          'g=d&' + \
          'a=%s&' % start_m + \
          'b=%s&' % start_d + \
          'c=%s&' % start_y + \
          'ignore=.csv'
    days = urllib.urlopen(url).readlines()
    data = [day[:-2].split(',') for day in days]
    return data
