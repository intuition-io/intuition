#!/usr/bin/python
# -*- coding: utf8 -*-

import urllib2
import os
import sys
import re
import time
import numpy as np
import sqlite3 as sql

database = "assets.db"
connection = sql.connect(database)
with connection:
    connection.row_factory = sql.Row
    cursor = connection.cursor()
    print '[DEBUG] Updating database...'
    buffer = 'drop table if exists computations'
    buffer = buffer.strip()
    cursor.execute(buffer)
    buffer = 'create table computations(date int, mean real, ma real)'
    buffer = buffer.strip()
    cursor.execute(buffer)
    buffer = 'insert into computations values(?, ?, ?)'
    buffer = buffer.strip()
    data = [[0, 4.3, 0.2]]
    cursor.executemany(buffer, data)
