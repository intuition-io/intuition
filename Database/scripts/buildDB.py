import ipdb as pdb

import sys
import os

import pandas as pd
import pytz

sys.path.append(str(os.environ['QTRADE']))
from pyTrade.data.QuantDB import QuantSQLite, Fields
from pyTrade.data.DataAgent import DataAgent


def fillQuotes(tickers, timestamp):
    ''' Download missing ticker data according
    to the given timestamp '''
    agent = DataAgent(['remote', 'database'], lvl='info')
    agent.getQuotes(tickers, Fields.QUOTES, index=timestamp, save=True)
    if agent.connected['database']:
        agent.db.close(commit=True)

if __name__ == '__main__':
    db = QuantSQLite('stocks.db')
    print db.execute('select sqlite_version()')
    db.queryFromScript('scriptBuild.sql')
    db.close()

    timestamp = pd.date_range(pd.datetime(2000, 1, 1, tzinfo=pytz.utc),
                              pd.datetime(2012, 12, 31, tzinfo=pytz.utc),
                              freq=pd.datetools.BDay())
    tickers = ['starbucks', 'google', 'apple', 'altair']
    fillQuotes(tickers, timestamp)
