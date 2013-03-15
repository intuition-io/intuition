Changelog
=========

13-03-2013
----------
- Some installation details added
- databot and sqlite files moved to playground
- ppQuanTrade/data/dump_sql.csv for building database from scratch
- Trello project management
- database manager script to manipulate easily available stocks
- New wiki pages : Installation, contribution
- Fixed automatic R installation (still lib issue)
- Added logger (futile.logger) in R scripts
- Created Positions table associated with portfolio
- Vocal goodies
- Added automatic set of Benchmark and timezone parameters for simulation
- Added in config.sh a line exporting in python path zipline and neuronquant libs. 
- Therefore removed in code sys.path.append(os.envion['QTRADE'])
- Storage and recuperation on-the-fly of multiple portfolios
- Generic to_dict() function for message and storage improvements
- Portfolio manager abstract class is able to handle asynchronous communications
- Change datamodel date fields with datetime too fix truncate issue


11-03-2013
----------
- Database can process any symbol, worldwide, including funds and becnhmarks
- Exchange option for the backtest
- Portfolio initial amount option (going with new way of initializing backtest)
- server/shiny-backtest/global.R: Access now mysql setup through config/mysql.cfg
- Every parameters relative to network were moved from server to config directory (default.json file). Node.js and R acceses it from here now.
- Added SortinoRatio and Information fields in Metrics table
- Added Portfolio table (bug with associated Positions table)
- Correct format message for shiny communication with backend, but error while broker reading
- Introduced mailbox interaction, rss reader, vocal synthetization and recognition (Vocal github repos, soon integrated)
- New funky bugs to fix
