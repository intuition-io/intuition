import sys
import os
import datetime as dt
import ipdb as pdb
import pytz

import pandas as pd
from pandas import DataFrame, Panel
import numpy as np

import qstkutil.qsdateutil as du
import qstkutil.DataAccess as da

sys.path.append(os.environ['QTRADE'])
from neuronquant.utils.logger import LogSubsystem
from neuronquant.data.QuantDB import QuantSQLite, Fields
from neuronquant.data.remote import Fetcher


class DataAgent(object):
    ''' Quote object - fill everything related:
            name, code, current value, bought value,
            market, actions owned,
            and date, open, close, volume, of asked period'''
    def __init__(self, sources=None, tz=pytz.utc, logger=None, lvl='debug'):
        self.tz = tz
        if logger is None:
            self._logger = LogSubsystem(DataAgent.__name__, lvl).getLog()
        else:
            self._logger = logger
        self.connected = {'remote': False, 'database': False, 'csv': False}
        if isinstance(sources, list):
            self.connectTo(sources, lvl=lvl, timezone=tz, logger=logger)

    def connectTo(self, connections, **kwargs):
        ''' Set up allowed data sources '''
        tz = kwargs.get('timezone', self.tz)
        log = kwargs.get('logger', None)
        lvl = kwargs.get('lvl', 'debug')
        if 'database' in connections:
            db_name = kwargs.get('db_name', str(os.environ['QTRADEDB']))
            self.db = QuantSQLite(db_name, timezone=tz, logger=log, lvl=lvl)
            self._logger.info('Database location provided, Connected to %s' % db_name)
            self.connected['database'] = True
        if 'remote' in connections:
            self.remote = Fetcher(timezone=tz, logger=log, lvl=lvl)
            self.connected['remote'] = True
        if 'csv' in connections:
            raise NotImplementedError()

    def _makeIndex(self, args):
        ''' Take getQuotes input and produce suitable index '''
        #TODO implement elapse
        start_day = args.get('start', None)
        end_day = args.get('end', dt.datetime.now(self.tz))
        delta = args.get('delta', self._guessResolution(start_day, end_day))
        period = args.get('period', None)
        if period:
            if not start_day:
                start_day = end_day - period
        if not start_day:
            if not delta:
                start_day = dt.datetime.now(self.tz).date()
                delta = pd.datetools.Minute()
            else:
                self._logger.error('** No suitable date informations provided')
                return None
        return pd.date_range(start=start_day, end=end_day, freq=delta)

    def _inspectDB(self, ticker, request_idx, fields=Fields.QUOTES):
        ''' Check available df in db, according to the requested index '''
        self._logger.info('Inspecting database.')
        assert (isinstance(ticker, str))
        assert (isinstance(request_idx, pd.Index))
        assert (isinstance(fields, list))
        #TODO comparisons are too strics
        #TODO identificate NaN columns, that will erase everything at dropna
        if not self.connected['database']:
            self._logger.info('No database access allowed.')
            return DataFrame(), request_idx

        db_index = self.db.getDataIndex(ticker, fields, summary=False)
        if not isinstance(db_index, pd.Index):
            self._logger.info('No quotes stored in database.')
            return DataFrame(), request_idx
        elif db_index.freq > request_idx.freq and not db_index.freq == request_idx.freq:
            self._logger.info('Superior asked frequency,\
                    dropping and downloading along whole timestamp')
            return DataFrame(), request_idx
        else:
            if db_index[0] > request_idx[0] and db_index[-1] < request_idx[-1]:
                return DataFrame(), request_idx
                raise NotImplementedError()
                #TODO Two different timestamps to download !
                #to dl: start_day -> first_db_date and last_db_date -> end_day
            else:
                #NOTE Intersection and other seemed cool but don't work
                if db_index[0].hour != 0:
                    db_index = pd.date_range(db_index[0] - pd.datetools.relativedelta(hours=db_index[0].hour),
                            db_index[-1] - pd.datetools.relativedelta(hours=db_index[0].hour), freq=db_index.freq)
                intersect = db_index & request_idx
                #start_to_get = intersect[0] - request_idx.freq
                #if not start_to_get.tzinfo:
                    #self.tz.localize(start_to_get)
                #idx_to_get = pd.date_range(start_to_get, intersect[-1], freq=request_idx.freq)
                idx_to_get = pd.date_range(intersect[0] - request_idx.freq,
                                           intersect[-1], freq=request_idx.freq)
                if idx_to_get is None or idx_to_get.size == 0:
                    self._logger.info('No quotes available in database.')
                    return DataFrame(), request_idx
                #NOTE try union minus intersect
                #TODO getQuotesDB and others take care of dataframe cast and fields cut
                if db_index[0] > request_idx[0]:
                    idx_to_dl = request_idx[request_idx < idx_to_get[0]]
                else:
                    idx_to_dl = request_idx[request_idx > idx_to_get[-1]]
                db_df = DataFrame(self.db.getQuotesDB(ticker, idx_to_get),
                                  columns=fields).dropna()
                if not db_df.index.tzinfo:
                    db_df.index.tz_localize(self.tz)
        return db_df, idx_to_dl

    #TODO each retriever, remote and db, takes care of dropna and columns
    def getQuotes(self, tickers, fields=Fields.QUOTES, index=None, **kwargs):
        '''
        @summary: retrieve google finance data asked while initializing
        and store it: Date, open, low, high, close, volume
        @param quotes: list of quotes to fetch
        @param fields: list of fields to store per quotes
        @param index: pandas.Index object, used for dataframes
        @param kwargs.start: date or datetime of the first values
               kwargs.end: date or datetime of the last value
               kwargs.delta: datetime.timedelta object, period of time to fill
               kwargs.save: save to database downloaded quotes
               kwargs.reverse: reverse companie name and field in panel
               kwargs.symbols
               kwargs.markets
        @return a panel/dataframe/timeserie like close = data['google']['close'][date]
        '''
        ''' ----------------------------------------------------------------------------'''
        ''' ----------------------------------  Index check and build  -----------------'''
        #FIXME reversed dataframe could be store in database ?
        df      = dict()
        save    = kwargs.get('save', False)
        reverse = kwargs.get('reverse', False)
        markets = kwargs.get('markets', None)
        symbols = kwargs.get('symbols', None)
        if not isinstance(index, pd.DatetimeIndex):
            index = self._makeIndex(kwargs)
            if not isinstance(index, pd.DatetimeIndex):
                return None
        if not index.tzinfo:
            index = index.tz_localize(self.tz)
        assert (index.tzinfo)

        if self.connected['database']:
            symbols, markets = self.db.getTickersCodes(tickers)
        elif not symbols or not markets:
            self._logger.error('** No database neither informations provided')
            return None

        for ticker in tickers:
            if not ticker in symbols:
                self._logger.warning('No code availablefor {}, going on'.format(ticker))
                continue
            self._logger.info('Processing {} stock'.format(ticker))

            ''' ----------------------------------------------------------------------------'''
            ''' ----------------------------------------------  Database check  ------------'''
            db_df, index = self._inspectDB(ticker, index, fields)
            assert (index.tzinfo)
            if not db_df.empty:
                assert (db_df.index.tzinfo)
                if index.size == 0:
                    save       = False
                    df[ticker] = db_df
                    continue

            ''' ----------------------------------------------------------------------------'''
            ''' ----------------------------------------------  Remote retrievers  ---------'''
            self._logger.info('Downloading missing data, from {} to {}'
                              .format(index[0], index[-1]))
            #FIXME No index.freq for comaprison?
            #if (index[1] - index[0]) < pd.datetools.timedelta(days=1):
            if index.freq > pd.datetools.BDay():
                self._logger.info('Fetching minutely quotes ({})'.format(index.freq))
                #TODO truncate in the method
                network_df = DataFrame(self.remote.getMinutelyQuotes(
                                       symbols[ticker], markets[ticker], index),
                                       columns=fields).truncate(after=index[-1])
            else:
                network_df = DataFrame(self.remote.getHistoricalQuotes(
                                       symbols[ticker], index), columns=fields)

            ''' ----------------------------------------------------------------------------'''
            ''' ----------------------------------------------  Merging  -------------------'''
            if not db_df.empty:
                self._logger.debug('Checking db index ({}) vs network index ({})'
                                   .format(db_df.index, network_df.index))
                if db_df.index[0] > network_df.index[0]:
                    df[ticker] = pd.concat([network_df, db_df])
                else:
                    df[ticker] = pd.concat([db_df, network_df]).sort_index()
            else:
                df[ticker] = network_df

        ''' ----------------------------------------------------------------------------'''
        ''' ----------------------------------------------  Manage final panel  --------'''
        data = Panel.from_dict(df, intersect=True)
        if save:
            #TODO: accumulation and compression of data issue, drop always true at the moment
            if self.connected['database']:
                self.db.updateStockDb(data, Fields.QUOTES, drop=True)
            else:
                self._logger.warning('! No database connection for saving.')
        if reverse:
            return Panel.from_dict(df, intersect=True, orient='minor')
        #NOTE if data used here, insert every FIELD.QUOTES columns
        #NOTE Only return Panel when one ticker and/or one field ?
        return Panel.from_dict(df, intersect=True)

    def _guessResolution(self, start, end):
        if not start or not end:
            return None
        elapse = end - start
        if abs(elapse.days) > 5 and abs(elapse.days) < 30:
            delta = pd.datetools.BDay()
        elif abs(elapse.days) <= 5 and abs(elapse.days) > 1:
            delta = pd.datetools.Hour()
        elif abs(elapse.days) >= 30:
            delta = pd.datetools.BMonthEnd(round(elapse.days / 30))
        else:
            delta = pd.datetools.Minute(10)
        self._logger.info('Automatic delta fixing: {}'.format(delta))
        return delta

    def load_from_csv(self, tickers, index, fields=Fields.QUOTES, **kwargs):
        ''' Return a quote panel '''
        #TODO Replace adj_close with actual_close
        #TODO Add reindex methods, and start, end, delta parameters
        reverse = kwargs.get('reverse', False)
        verbose = kwargs.get('verbose', False)
        if self.connected['database']:
            symbols, markets = self.db.getTickersCodes(tickers)
        elif not symbols:
            self._logger.error('** No database neither informations provided')
            return None
        timestamps = du.getNYSEdays(index[0], index[-1], dt.timedelta(hours=16))
        csv = da.DataAccess('Yahoo')
        df = csv.get_data(timestamps, symbols.values(), fields, verbose=verbose)
        quotes_dict = dict()
        for ticker in tickers:
            j = 0
            quotes_dict[ticker] = dict()
            for field in fields:
                serie = df[j][symbols[ticker]].groupby(index.freq.rollforward).aggregate(np.mean)
                #TODO add a function parameter to decide what to do about it
                clean_serie = serie.fillna(method='pad')
                quotes_dict[ticker][field] = clean_serie
                j += 1
        if reverse:
            return Panel.from_dict(quotes_dict, intersect=True, orient='minor')
        return Panel.from_dict(quotes_dict, intersect=True)

    def help(self, category):
        #TODO: stuff to know like fields and functions
        print('{} help'.format(category))


''' Example
if __name__ == '__main__':
    dataobj = DataAgent('stocks.db')        # Just needs the relative path to Database directory
    startday = pd.datetime(2011,6,20)      #in db: 2011-12-05
    endday = pd.datetime(2012,4,1)          #in db: 2012-6-1
    delta = dt.timedelta(days=3)            #in db: 1
    data = dataobj.getQuotes(['altair'], ['open', 'volume'], \
            start=startday, end=endday, delta=delta)
    print('================\n{}'.format(data['altair']['open'].head()))
    #summary = dataobj.getSnaphot(['google', 'apple'], light=true)
    #print '(light) Google variation: %s' % summary['google'][Alias.VARIATION]
    #summary = dataobj.getSnaphot(['google', 'apple'], light=False)
    #print '(heavy) Apple market cap: %s' % summary['apple']['market_cap']

    #dataobj.db.updateStockDb(data, Fields.QUOTES, drop=True)
    #first_date, last_date, freq = dataobj.db.getDataIndex('google', summary=True)
    #print('Data from {} to {} with an interval of {}'.format(first_date, last_date, freq))
    #quotes = DataFrame(dataobj.db.getQuotesDB('google', start=startday,\
            #end=endday, delta=delta), columns=['open', 'volume']).dropna()
    #print quotes.head()
    dataobj.db.close(commit=True)
'''
