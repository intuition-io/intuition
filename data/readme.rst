Description
-----------
    * feeds.db stores news (from twitter for now) for further natural language processing
    * stocks.db is the sqlite database
    * QSDATA, inspired by qstk project, stores csv files

nota Mysql
----------
    mysqladmin -u root
    mysql> set password for 'root'@'localhost' = password('password');
    mysql> create user 'user'@'host' identified by 'password'
    mysql> grant all privileges on *.* to 'user'@'host'
    mysql> create database stock_data;
    connection: mysql -h localhost -u root -p
    mysql> \u stock_data ;

    mysql stock_data -p
    show tables ; 
    show fields from Symbols ; 
    select * from Symbols limit 2;
    select * from Symbols where Symbols.Ticker='index' ; 
    delete from Symbols where Symbols.Ticker='index' ;

