# SQLite wrapper
import time
import Queue
import threading
import sqlite3 as sql

from decorators import *

from LogSubsystem import LogSubsystem

'''---------------------------------------------------------------------------------------
SQLite Wrapper
---------------------------------------------------------------------------------------'''
class SQLiteWrapper(threading.Thread):
    def __init__(self, filename="assets.db", logger=None):
        super(SQLiteWrapper, self).__init__()
        self._filename = filename
        self._queue = Queue.Queue()
        self._stopped = threading.Event()
        self._n = 0
        self.start()
        if logger == None:
            self._logger = LogSubsystem(__name__, 'debug').getLog()
        else:
            self._logger = logger
        
    def _log_debug(self, msg):
        if self._logger != None:
            self._logger.debug(msg)
        else:
            print "%-8s %s" % ("DEBUG:", msg)
            
    def _log_info(self, msg):
        if self._logger != None:
            self._logger.info(msg)
        else:
            print "%-8s %s" % ("INFO:", msg)
            
    def _log_error(self, msg):
        if self._logger != None:
            self._logger.error(msg)
        else:
            print "%-8s %s" % ("ERROR:", msg)
        
    def run(self):
        self._log_debug("Database thread started.")
        self._query_lock = threading.Lock()
        self._connection = sql.connect(self._filename)
        self._connection.row_factory = sql.Row
        self._connection.text_factory = str
        self._log_info("Database connection to %s established." % self._filename)
        cursor = self._connection.cursor()
        
        while True:
            cmd, params, many, q = self._queue.get()
                
            if cmd == "close":
                self._log_debug("Database got 'close' command.")
                q.put([])
                break
            elif cmd == "commit":
                self._log_debug("Database got 'commit' command.")
                self._connection.commit()
                self._log_debug("Database changes committed.")
                q.put([])
                continue
                
            res = []
            try:
                if ( many ):
                    cursor.executemany(cmd, params)
                else:
                    cursor.execute(cmd, params)
                res = cursor.fetchone()
            except sql.Error, e:
                self._log_error("Database error: '%s'." % e.args[0])
            q.put(res)
        
        self._stopped.set()
        self._connection.close()
        self._log_info("Database connection closed.")
        self._log_debug("Database thread terminated.")
                
    def close(self):
        """
        Close the database connection and terminate thread.
        """
        self.execute("close")
        
    def commit(self):
        """
        Commit changes.
        """
        self.execute("commit")
        
    def execute(self, cmd, params=tuple()):
        """
        Execute the command cmd. '?'s in the command are replaced by the
        params tuple's content.
        """ 
        self._n += 1
        n = self._n
        many = False
        try:
            if type(params[0]) is type(list()):
                self._log_debug('Executing several queries at a time')
                many = True
        except:
            many = False
        start = time.time()
        if not self._stopped.isSet():
            q = Queue.Queue()
            self._queue.put((cmd, params, many, q))
            res = q.get()
            dur = time.time() - start
            self._log_debug("Database query %s executed in %s seconds." % (n, \
                                                                           dur))
            return res
        return None
        
    def getTables(self):
        """
        Returns a list of table names currently in the database.
        """
        res = self.execute("SELECT tbl_name FROM sqlite_master")
        tables = []
        for row in res:
            name = row[0]
            tables.append(name)
        return tables

    def getData(self, table, id, fields):
        '''
        Return data as a list in specified location
        '''
        statement = 'select %s' % fields[0] 
        for item in fields[1:]:
            statement = statement + ', ' + item 
        tmp = ' from %s where %s=:%s' % (table, id.keys()[0], id.keys()[0] )
        statement += tmp
        self._logger.debug(statement)
        res = self.execute(statement, id)
        return res

    def finalize(self):
        self.execute('commit')
        self.close()

    def __def__(self):
        self.finalize()



'''---------------------------------------------------------------------------------------
Usage Exemple
---------------------------------------------------------------------------------------'''
'''
if __name__ == '__main__':
  database = SQLiteWrapper("assets.db", log)
  database.execute("select * from stocks")
  database.execute("select * from basic")
  tables = database.getTables()
  print tables
  database.close()
'''
