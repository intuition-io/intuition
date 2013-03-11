Changelog
=========

11-03-2013
----------
- Database can process any symbol, worldwide.
- Exchange option for the backtest
- Portfolio initial amount option (going with new way of initializing backtest)
- server/shiny-backtest/global.R: Access now mysql setup through config/mysql.cfg
- Every parameters relative to network were moved from server to config directory (default.json file). Node.js and R acceses it from here now.
- Added SortinoRatio and Information fields in Metrics table
- Added Portfolio table (bug with associated Positions table)
- Correct format message for shiny communication with backend, but error while broker reading
- Introduced mailbox interaction, rss reader, vocal synthetization and recognition (Vocal github repos, soon integrated)
- New funky bugs to fix
