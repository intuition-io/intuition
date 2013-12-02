Description
-----------

* feeds.db stores news (from twitter for now) for further natural language processing
* stocks.db is an sqlite database
* QSDATA, inspired by qstk project, stores csv files

nota Mysql
----------

```
$ mysqladmin -u root
mysql> set password for 'root'@'localhost' = password('password');
mysql> create user 'user'@'host' identified by 'password'
mysql> grant all privileges on *.* to 'user'@'host'
mysql> create database stock_data;
#connection:
$ mysql -h localhost -u root -p
mysql> \u stock_data ;

$ mysql stock_data -p
mysql> show tables ;
mysql> show fields from Symbols ;
mysql> select * from Symbols limit 2;
mysql> select * from Symbols where Symbols.Ticker='index' ;
mysql> delete from Symbols where Symbols.Ticker='index' ;
```
