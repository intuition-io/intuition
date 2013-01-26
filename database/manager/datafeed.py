#!/usr/bin/env python
""" datafeed.py
Data sources
"""
from database import Client
import pandas as pd


class DataFeed(object):
    """
    API for using database quotes into application
    """
    def __init__(self):
        self.stock_db = Client()

    def get_quotes(self, tickers, start_date=None, end_date=None):
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
        if isinstance(tickers, str):
            tickers = [tickers]
        df_tmp = dict()
        for ticker in tickers:
            infos = self.infos(ticker)
            data = self.stock_db.get_quotes(infos.Ticker, start_date=start_date, end_date=end_date)
            index = pd.DatetimeIndex([data[i].Date for i in range(len(data))])
            df_tmp[ticker] = pd.Series([data[i].AdjClose for i in range(len(data))], index=index)
        return pd.DataFrame(df_tmp)

    def infos(self, ticker):
        return self.stock_db.get_infos(name=ticker)
