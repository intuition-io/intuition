drop table if exists cac40 ;
drop table if exists nasdaq ;

drop table if exists properties ;
create table properties(Id int, ticker text, symbol text, market text, country_code text, ccy_code text, rss_url text) ;
insert into properties values(1, 'accor', 'AC', 'EPA', 'fr', 'eur', '') ;
insert into properties values(2, 'lvmh', 'MC', 'EPA', 'fr', 'eur', '') ;
insert into properties values(3, 'eads', 'EAD', 'EPA', 'fr', 'eur', '') ;
insert into properties values(4, 'google', 'GOOG', 'NASDAQ', 'us', 'usd', '') ;
insert into properties values(5, 'apple', 'AAPL', 'NASDAQ', 'us', 'usd', '') ;
insert into properties values(6, 'altair', 'ALTI', 'NASDAQ', 'us', 'usd', '') ;

drop table if exists indices ;
create table indices(Id int, ticker text, symbol text, market text, country_code text, ccy_code text, rss_url text) ;
insert into indices values(1, 'cac40', 'PX1', 'INDEXEURO', 'fr', 'eur', '') ;
insert into indices values(2, 'nasdaq', '.IXIC', 'INDEXNASDAQ', 'us', 'usd', '') ;
