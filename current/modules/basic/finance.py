#!/usr/bin/python
# -*- coding: utf8 -*-

import urllib2
import os
import sys
import re
import time
import numpy as np
import sqlite3 as sql

class Quote:
    ''' Quote object - fill everything related:
            name, code, current value, bought value,
            market, actions owned,
            and date, open, close, volume, of asked period'''
    def __init__(self, quote, database):
        self.connection = sql.connect(database)
        with self.connection:
            self.connection.row_factory = sql.Row
            self.cursor = self.connection.cursor()
            self.cursor.execute('select symbol, market, rss from stocks where ticker=:ticker', {"ticker": quote})
            row = self.cursor.fetchone()
            if ( row == None ):
                print '[INFO] No reference found in database, exiting...'
                sys.exit(-1)
            else:
                self.symbol = row['symbol']
                self.market = row['market']
                self.rss_source = row['rss']
                self.rss = 'http://www.google.com/finance/company_news?q=' + row['market'] + ':' + row['symbol'] + '&output=rss'
        self.name = quote

    def download(self, days, precision):
        ''' analyse google finance data asked while initializing
        and store it: Date, open, low, high, close, volume '''
        # Getting the data
        url = 'http://www.google.com/finance/getprices?q=' + self.symbol + '&x=' + self.market + '&p=' + str(days) + 'd&i=' + str(precision*61)
        print '[DEBUG] Retrieving data from', url
        try:
            page = urllib2.urlopen(url)
        except IOError:
            print '[!!] Bad url: %s' %url
            sys.exit(1)
        cpt = 1
        feed = ''
        while (re.search('^a', feed) == None):
            feed = page.readline()
        while ( feed != '' ):
            infos = feed.split(',')
            if ( cpt == 1 ):
                self.data = np.array([[float(infos[0][1:]), float(infos[4]), float(infos[3]), float(infos[2]), float(infos[1]), float(infos[5])]], dtype=np.float32)
                print self.data
            else:
                self.data = np.append(self.data, [[float(infos[0][1:]), float(infos[4]), float(infos[3]), float(infos[2]), float(infos[1]), float(infos[5])]], axis=0)
            feed = page.readline()
            cpt += 1

    def epochToDate(self, epoch):
        ''' Convert seconds of epoch time to date POSIXct format %Y-%M-%D %H:%m '''
        return time.strftime("%Y-%m-%d %H:%M", time.localtime(epoch))


    def updateDb(self):
        ''' store quotes and information '''
        ''' Updating index table '''
        print '[DEBUG] Updating rule database...'
        buffer = 'drop table if exists ' + self.name
        buffer = buffer.strip()
        uvalue = self.data[self.data.shape[0]-1, 4]
        uvariation = self.computeVariation()
        ubegin = self.epochToDate(self.data[0,0])
        uend = self.epochToDate(self.data[self.data.shape[0]-1, 0])
        with self.connection:
            self.cursor.execute('update stocks set value=?, variation=?, begin=?, end=? where ticker=?', (uvalue, uvariation, ubegin, uend, self.name))
            ''' Updating values stock table '''
            self.cursor.execute(buffer)
            buffer = 'create table ' + self.name + '(date int, open real, low real, high real, close real, volume int)'
            buffer = buffer.strip()
            self.cursor.execute(buffer)
            buffer = 'insert into ' + self.name + ' values(?, ?, ?, ?, ?, ?)'
            buffer = buffer.strip()
            self.cursor.executemany(buffer, self.data)


    def computeVariation(self):
        ''' return day variation '''
        return ((self.data[self.data.shape[0]-1, 4] - self.data[0,4])/self.data[0,4]) * 100


#TODO Add control commands
#TODO Resolve data problem for 30 days 60minutes
#date = time.strftime("%Y-%m-%d %H:%M", time.localtime(float(infos[0][1:])))    #see %c also and %m
