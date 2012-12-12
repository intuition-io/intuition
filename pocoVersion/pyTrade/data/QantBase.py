import sys

#TODO: environnement variable ?
sys.path.append('..')
from Utilities import LogSubSystem
from Utilities import DatabaseSubSystem

class QantBase(DatabaseSubSystem):
    """ 
    Specific database facilities fir quanTrade software 
    """
    def __init__(self, db_file='assets.db', logger=None):
        if logger == None:
            self._logger = LogSubSystem(__name__, 'debug').getLog()
        else:
            self._logger = logger
        # try super().__init__(bla bla)
        DatabaseSubSystem.__init__(self, db_file, self._logger)

    def updateStockDb(self, quotes):
        ''' 
        store quotes and information 
        '''
        self._logger.info('Updating database...')
        #TODO: Handling data accumulation and compression
        #TODO: Euh en fait tout changer
        uvariation = 0
        ubegin = quotes.index[0]
        uend = quotes.index[len(quotes)-1]
        uvalue = quotes['close'][uend]
        try:
            self._db.execute('update stocks set value=?, variation=?, begin=?, end=? \
                    where ticker=?', (uvalue, uvariation, ubegin, uend, self.name))
            res = self._db.execute('drop table if exists ' + self.name)
            self._db.execute('create table ' + self.name + \
                    '(date int, open real, low real, high real, close real, volume int)')
            for i in range(0, len(quotes)):
                raw = (quotes.index[i],
                    quotes['open'][i], 
                    quotes['close'][i], 
                    quotes['high'][i],
                    quotes['low'][i],
                    quotes['volume'][i])
                self._db.execute('insert into ' + self.name + ' values(?, ?, ?, ?, ?, ?)', raw)
        except:
            self._logger.error('While insering new values in database')
            self.finalize()
