/*
 * createdb.sql
 * Copyright (C) 2013 xavier <xavier@laptop-300E5A>
 *
 * Distributed under terms of the MIT license.
 */

CREATE database IF NOT EXISTS stock_data;
GRANT ALL PRIVILEGES ON stock_data.* to you@localhost identified by 'password'
