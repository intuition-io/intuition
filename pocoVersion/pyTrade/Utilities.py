#!/usr/bin/python
# -*- coding: utf8 -*-

# Logger class (obviously...)
import logging

# SQLite wrapper
import time
import Queue
import threading
import sqlite3 as sql


#TODO: reimplement fatal function with (colors ?) exit
'''---------------------------------------------------------------------------------------
Logger class
---------------------------------------------------------------------------------------'''
class LogSubSystem:
  ''' Trade logging version '''
  def __init__(self, name = '', lvl_str = "debug"):
    if lvl_str == "debug":
      lvl = logging.DEBUG
    elif lvl_str == "info":
      lvl = logging.INFO
    else:
      print '[DEBUG] __LogSubSystem__ : Unsupported mode, setting default logger level: debug'
      lvl = logging.DEBUG
    if name == '':
      self.logger = logging.getLogger()
    else:
      self.logger = logging.getLogger(name)
    self.logger.setLevel(lvl)
    self.setup(lvl)

  def setup(self, lvl = logging.DEBUG):
    self.formatter = logging.Formatter('[%(levelname)s] %(name)s :  %(message)s')

    ch = logging.StreamHandler()
    ch.setLevel(lvl)
    ch.setFormatter(self.formatter)
    self.logger.addHandler(ch)

    print('[DEBUG] __LogSubSystem__ : Logging initialized.')

  def addFileHandler(self, lvl = logging.DEBUG, file_store = 'pyTrade.log'):
    fh = logging.FileHandler(file_store)
    fh.setLevel(lvl)
    fh.setFormatter(self.formatter)
    self.logger.addHandler(fh)
    print('[DEBUG] __LogSubSystem__ : Logging file handler initialized.')

  def getLog(self):
    return self.logger



'''---------------------------------------------------------------------------------------
SQLite Wrapper
---------------------------------------------------------------------------------------'''
class DatabaseSubSystem(threading.Thread):
    def __init__(self, filename="assets.db", logger=None):
        super(DatabaseSubSystem, self).__init__()
        self._filename = filename
        self._queue = Queue.Queue()
        self._stopped = threading.Event()
        self._logger = logger
        self._n = 0
        self.start()
        
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



'''---------------------------------------------------------------------------------------
Usage Exemple
---------------------------------------------------------------------------------------'''
'''
if __name__ == '__main__':
  logSys = LogSubSystem(__name__, "debug")
  #logSys.addFileHandler()
  log = logSys.getLog()

  # 'application' code
  log.debug('SQLite fork wrapper test')

  database = DatabaseSubSystem("assets.db", log)
  database.execute("select * from stocks")
  database.execute("select * from basic")
  tables = database.getTables()
  print tables
  database.close()
'''

