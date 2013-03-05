Description
-----------
    * feeds.db stores news (from twitter for now) for further natural language processing
    * stocks.db is the sqlite database
    * QSDATA, inspired by qstk project, stores csv files


ChangeLog
---------
    add 'sys.path()' instad of relatives deps


nota Mysql
----------
    mysqladmin -u root -p status
    connection: mysql -h localhost -u root -p
    create database stock_data;
    \u stock_data ;
    exit

    mysql stock_data
    show tables ; 
    show fields from Symbols ; 
    select * from Symbols ;
    select * from Symbols where Symbols.Ticker='index' ; 
    delete from Symbols where Symbols.Ticker='index' ;

