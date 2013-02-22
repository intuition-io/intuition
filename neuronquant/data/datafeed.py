""" datafeed.py
Data sources
"""
import pandas as pd
import pytz
import random
import re
import sys
import os

sys.path.append(os.environ['QTRADE'])
from logbook import Logger
from neuronquant.data.database import Client

log = Logger('DataFeed')


class DataFeed(object):
    """
    API for using database quotes into application
    """
    def __init__(self, level='debug'):
        self.stock_db = Client()

    def quotes(self, tickers, start_date=None, end_date=None, download=False):
        """ Get a series of quotes
        Return a list of quotes for the given security from start_date to
        end-date
        :param ticker: Ticker symbol of the security to quote.
        :param start_date: Starting date of quote list as a string or
        ``Datetime.date`` object.
        :param end_date: Ending date of quote list as a string or a
        ``Datetime.date`` object.
        :returns: List of quotes for the given security and date range
        """
        #NOTE Always retrieve adjusted close ?
        #TODO Frequency management
        #TODO No available symbols should be downloaded (with a parameter)
        if isinstance(tickers, str):
            tickers = [tickers]
        df_tmp = dict()
        for ticker in tickers:
            symbol = self.guess_name(ticker)
            log.info('Retrieving {} quotes from database'.format(ticker))
            data = self.stock_db.get_quotes(symbol, start_date=start_date, end_date=end_date, dl=download)
            if data is None:
                continue
            index = pd.DatetimeIndex([data[i].Date for i in range(len(data))])
            index = index.tz_localize(pytz.utc)
            #NOTE Symbol or name as columns ?
            df_tmp[ticker] = pd.Series([data[i].AdjClose for i in range(len(data))], index=index)
        return pd.DataFrame(df_tmp)

    def infos(self, ticker):
        symbol = self.guess_name(ticker)
        return self.stock_db.get_infos(symbol=symbol)

    def random_stocks(self, n=5):
        ''' Return n random stock names from database '''
        log.info('Generating {} random stocks'.format(n))
        stocks = self.stock_db.available_stocks()
        random.shuffle(stocks)
        if n > len(stocks):
            log.warning('{} asked symbols but only {} availables'.format(n, len(stocks)))
            n = len(stocks)
        return stocks[:n]

    def guess_name(self, partial_input):
        #NOTE Everything could work with symbols, under this interface
        ''' Find the closest math of partial_input in stocks database, and return its symbol '''
        match = [name for name in self.stock_db.available_stocks(key='name') if re.match(partial_input, name, re.IGNORECASE) is not None]
        if not match:
            log.debug('No matching name, trying symbol list...')
            match = [name for name in self.stock_db.available_stocks(key='symbol') if re.match(partial_input, name, re.IGNORECASE) is not None]
            if match:
                infos = self.stock_db.get_infos(symbol=match[0])
            else:
                return partial_input
        else:
            infos = self.stock_db.get_infos(name=match[0])
        return infos.Ticker
