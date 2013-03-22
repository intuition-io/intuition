#
# Copyright 2012 Xavier Bruhiere
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


""" datafeed.py
Data sources
"""
import pandas as pd
import pytz
import random
import re

import logbook
from neuronquant.data.database import Client

log = logbook.Logger('DataFeed')


class DataFeed(object):
    """
    API for using database quotes into application
    """
    def __init__(self):
        self.stock_db = Client()

    def saved_portfolios(self, names):
        '''
        Fetch from database a previously stored portfolio
        _________________________________________________
        Parameter
            names: str
                Portfolios are stored with a name as unique ID,
                get those
        _________________________________________________
        Return
            A Portfolio database model if name was found,
            None otherwize
        '''
        lonely = False
        if isinstance(names, str):
            names = [names]
            lonely = True
        df_tmp = dict()

        for name in names:
            log.info('Retrieving {} portfolio from database'.format(name))
            data = self.stock_db.get_portfolio(name)
            if data is None:
                continue
            if lonely:
                return pd.Series(data.__dict__)
            df_tmp[name] = pd.Series(data.__dict__)

        if df_tmp:
            return pd.DataFrame(df_tmp)
        return pd.DataFrame()

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
            df_tmp[ticker] = pd.Series([data[i].AdjClose for i in range(len(data))], index=index)
        return pd.DataFrame(df_tmp)

    def infos(self, ticker):
        symbol = self.guess_name(ticker)
        return self.stock_db.get_infos(symbol=symbol)

    def random_stocks(self, n=5, exchange=''):
        ''' Return n random stock names from database '''
        log.info('Generating {} random stocks'.format(n))
        stocks = []
        #NOTE Can't consider the whole universe of stocks, will bug with exchange=None
        if isinstance(exchange, str):
            exchange = [exchange]
        for ex in exchange:
            stocks.extend(self.stock_db.available_equities(exchange=ex))
        random.shuffle(stocks)
        if n > len(stocks):
            log.warning('{} asked symbols but only {} availables'.format(n, len(stocks)))
            n = len(stocks)
        return stocks[:n]

    #TODO Implement sophisticated criteria choice, here only random (imagine sharpe ration rank)
    def get_universe(self, exchange=None, limit=10):
        '''
        Get a set of stocks, as the universe on which we will trade
        ___________________________________________________________
        Parameters
            exhange: str or list(...)
                Market(s) to search for stocks
            limit: int
                Limit of stocks to provide (big amount can make the simulation a mess)
        ___________________________________________________________
        Return
            stocks: list(limit | max found)
                Provide stock list according to specified criteria
        '''
        log.info('Generating stock universe')
        return self.random_stocks(n=limit, exhange=exchange)

    def guess_name(self, partial_input):
        ''' Find the closest math of partial_input in stocks database, and return its symbol '''
        match = [name for name in self.stock_db.available_equities(key='name') if re.match(partial_input, name, re.IGNORECASE) is not None]
        if not match:
            log.debug('No matching name, trying symbol list...')
            match = [name for name in self.stock_db.available_equities(key='symbol') if re.match(partial_input, name, re.IGNORECASE) is not None]
            if match:
                infos = self.stock_db.get_infos(symbol=match[0])
            else:
                return None
        else:
            infos = self.stock_db.get_infos(name=match[0])
        return infos.Ticker
