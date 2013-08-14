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


#NOTE SQLite (as well as DataAgent) is deprecated for now (MySQL is used instead) and will be re-written later with SQLAlchimy

import sys
import os

import pandas as pd
import pytz

sys.path.append(os.environ['QTRADE'])
from neuronquant.data.QuantDB import QuantSQLite, Fields
from neuronquant.data.databot import DataAgent


def fill_quotes(tickers, timestamp):
    ''' Download missing ticker data according
    to the given timestamp '''
    agent = DataAgent(['remote', 'database'], lvl='info')
    agent.getQuotes(tickers, Fields.QUOTES, index=timestamp, save=True)
    if agent.connected['database']:
        agent.db.close(commit=True)

if __name__ == '__main__':
    # Configuration
    assert len(sys.argv) == 2
    if sys.argv[1] == 'twitter':
        database = 'feeds.db'
        script = 'twitterBuild.sql'
    elif sys.argv[1] == 'stocks':
        database = 'stocks.db'
        script = 'stocksBuild.sql'
    else:
        raise NotImplementedError()

    # Open or create the desired sqlite database
    db = QuantSQLite(database)
    # Test everything is alright
    print db.execute('select sqlite_version()')

    # Execute sql script
    db.queryFromScript(script)
    db.close()

    if sys.argv[1] == 'stocks':
        # getQuotes() method will fetch data that is not available in database and then store it
        timestamp = pd.date_range(pd.datetime(2005, 1, 1, tzinfo=pytz.utc),
                                  pd.datetime(2012, 11, 30, tzinfo=pytz.utc),
                                  freq=pd.datetools.BDay())
        tickers = ['starbucks', 'google', 'apple', 'altair']
        fill_quotes(tickers, timestamp)

    elif sys.argv[1] == 'twitter':
        #TODO Use script in ppQuantrade/playground/nlp/twit.py
        raise NotImplementedError()
