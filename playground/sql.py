#!/usr/bin/python
# -*- coding: utf8 -*-

import sqlite3
import json
import sys

# Storing configuration file in python array
config = json.load(open('./config.json', 'r'))
#print config['share']['name']

assets_db = sqlite3.connect('assets.db')


infos = (
        (1,"archos",4.25,0.25,"stock","JXR","EPA","cac40","2012-06-22 09:00","2012-06-22 17h00","http://www.rss.com","test"),
        (2,"google",402.2,-0.5,"stock","GOOG","NYSE","NYSE","2012-06-22 09:00","2012-06-22 17h00","http://www.rss.com","test")
        )


with assets_db:
    assets_db.row_factory = sqlite3.Row     #For dictionary cursor
    assets_c = assets_db.cursor()

    assets_c.execute('drop table if exists stocks')
    assets_c.execute('CREATE TABLE stocks(id integer primary key, ticker text, value real, variation real, tag text, symbol text, market text, dependence text, begin text, end text, rss text, comment text)')
    assets_c.executemany('insert into stocks values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', infos)

    # Some operation on the db
    uticker = 'google'
    umarket = 'NASDAQ'
    assets_c.execute('update stocks set market=? where ticker=?', (umarket, uticker))

    # Retrieving data
    # one entry
    '''
    assets_c.execute('select symbol, value from stocks where ticker=:ticker', {"ticker": uticker})
    row = assets_c.fetchone()
    print row[0], row[1]
    '''
    # Every entry
    '''
    assets_c.execute('select * from stocks')
    while True:
        row = assets_c.fetchone()
        if row == None:
            break
        print row['id'], row['ticker'], row['value']
        '''
    
    #assets_db.commit()
    #print 'Number of raws updated: %d' % assets_c.rowcount

    # Metadata
    '''
    # Show fields in table
    assets_c.execute('pragma table_info(stocks)')
    data = assets_c.fetchall()
    for d in data:
        print d[0], d[1], d[2]

    # Show fields name and values aligned
    assets_c.execute('select * from stocks')
    col_names = [cn[0] for cn in assets_c.description]
    rows = assets_c.fetchall()
    print '%s %-10s %s' % (col_names[0], col_names[1], col_names[2])
    for row in rows:
        print '%2s %-10s %s' % (row[0], row[1], row[2])
    '''
    # Show informations on tables in db
    '''
    assets_c.execute('select name from sqlite_master where type="table"')
    rows = assets_c.fetchall()
    for row in rows:
        print row
    '''
    ###############################################################################


    uticker = 'archos'
    assets_c.execute('select symbol, market from stocks where ticker=:ticker', {"ticker": uticker})
    row = assets_c.fetchone()
    print row[0], row[1]
    uvalue = '234.9'
    assets_c.execute('update stocks set value=? where ticker=?', (uvalue, uticker))
