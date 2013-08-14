/*
 * createdb.sql
 * Copyright (C) 2013 xavier <xavier@laptop-300E5A>
 *
 * Distributed under terms of the MIT license.
 */

-- Vagrant or remote configuration
-- On mysql server:
-- Comment the line in /etc/mysql/my.cnf beginning with bind 127.0.0.1
-- create user vagrant@10.0.3.228 identified by 'password';

CREATE database IF NOT EXISTS stock_data;
GRANT ALL PRIVILEGES ON stock_data.* to you@localhost identified by 'password'
