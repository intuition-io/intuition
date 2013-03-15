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


# SQLite wrapper
import time
import sqlite3 as sql

from decorators import *
from logger import LogSubsystem


'''---------------------------------------------------------------------------------------
SQLite Wrapper
---------------------------------------------------------------------------------------'''
class SQLiteWrapper(object):
    def __init__(self, filename="stocks.db", logger=None):
        super(SQLiteWrapper, self).__init__()
        self._db_name = filename
        if logger is None:
            self._logger = LogSubsystem(self.__class__.__name__, 'debug').getLog()
        else:
            self._logger = logger
        self._logger.info('Running sqlite python wrapper - version {} / {}'.format(sql.version, sql.sqlite_version))
        self._connection = sql.connect(self._db_name)
        self._connection.row_factory = sql.Row
        self._connection.text_factory = str
        self.cursor = self._connection.cursor()
        self._logger.info("Database connection to %s established." % self._db_name)
        self._n = 0
        self.connected = True

    def execute(self, cmd, params=tuple()):
        '''
        Execute the command cmd. '?'s in the command are replaced by the params tuple's content.
        '''
        cmd = cmd.lower()
        self._n += 1
        n = self._n
        many = False
        res = []
        try:
            if type(params[0]) is type(list()):
                self._logger.debug('Executing several queries at a time')
                many = True
        except:
            many = False
        start = time.time()
        try:
            if (many):
                self.cursor.executemany(cmd, params)
            else:
                self.cursor.execute(cmd, params)
            #FIXME where word is used in 'fetchone commands'(see isTableExists), matter ?
            if cmd.find('where') < 0:
                res = self.cursor.fetchall()
                #if len(res) == 1:
                    #res = res[0]
            else:
                res = self.cursor.fetchone()
                #NOTE Relevant ?
                #if len(res) == 1:
                    #res = res[0]
        except sql.Error, e:
            self._logger.error("Database error: '%s'." % e.args[0])
        dur = time.time() - start
        self._logger.debug("Database query %s executed in %s seconds." % (n, dur))
        return res

    def isTableExists(self, table_name):
        '''
        Check if the given table exists in the current connected database
        '''
        assert isinstance(table_name, str)
        #res = self.execute('SELECT COUNT(*) FROM sqlite_master \
                #WHERE type = "{}" AND name = "{}"'.format('table', table_name))
        #self._logger.debug('Table check result: {}'.format(res))
        #return (res == 1)
        return (table_name in self.getTables())

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

    def getData(self, table, idx, fields):
        '''
        Return data as a list in specified location
        '''
        #TODO: a .join() thing to do here
        statement = 'select %s' % fields[0]
        for item in fields[1:]:
            statement = statement + ', ' + item
        tmp = ' from %s where %s=:%s' % (table, idx.keys()[0], idx.keys()[0])
        statement += tmp
        self._logger.debug(statement)
        res = self.execute(statement, idx)
        return res

    def csvToDatabase(self, csv_file):
        '''
        @summary read a csv file and write it to connected database
        the name minus '.csv' will be the table, and the header (1st line) the columns
        '''
        table = csv_file[:csv_file.find('.csv')]
        print('Processing table {} ({})'.format(table, self._db_name))
        err = None
        return err

    def queryFromScript(self, filename):
        last_slash = self._db_name.rfind('/')
        script = '/'.join((self._db_name[:last_slash], 'scripts', filename))
        query = open(script, 'r').read()
        self._logger.info('Executing query: {}'.format(query))
        self.cursor.executescript(query)

    def finalize(self):
        self.commit(close=True)

    def commit(self):
        """ Commit changes."""
        self._logger.debug("Database got 'commit' command.")
        self._connection.commit()
        self._logger.debug("Database changes committed.")

    def close(self, commit=False):
        ''' ! this function close database without commit '''
        if commit:
            self._connection.commit()
        self._logger.info('Database got close command')
        self._connection.close()
        self.connected = True

    def __del__(self):
        self._logger.info('Deleting object')
        if self.connected:
            self.close(commit=False)


'''---------------------------------------------------------------------------------------
Usage Exemple
---------------------------------------------------------------------------------------'''
'''
if __name__ == '__main__':
    db = SQLiteWrapper("stocks.db")
    print db.execute('SELECT SQLITE_VERSION()')
    db.queryFromScript('test.sql')
    db.close()   # a good habbit but __del__ handles that
'''
