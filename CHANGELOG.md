Changelog
=========

n.n.n / 2013-06-01 
==================

 * datasource plug strategie
 * Multiple nodes live running
 * live trade fixes: day_count error and logs
 * New strategies, server log and better grid support
 * Gird and Dashboard new features refactored
 * Ready for grid mode
 * Merge branch 'develop' of 192.168.0.17:dev/projects/ppQuanTrade into develop
 * fix
 * trade() works
 * fixes, fixes, and team_dashboard integration !
 * intermediate commit before computer storm
 * new algos implementation, and many playground adds
 * quandl integration, more relevant application directory and scripts
 * Fixes and reshapes, timezone handler, android notifs
 * Functionnal live-trading, server and client side
 * Presentation project, fixs, optimization update and began data reshape
 * clean refactoring branch, splitted pre and post simulation, pip-tools, some fixes
 * Engine and interface reshaped, live benchmark implemented, installation improvements
 * forex implementation, new live source and load_market_data for live trading, new utilities, new database schema, new config dir
 * better wiki and code, began database reshape, portfolio stoorage and load, asynchronous manager communication, improve tradingEnv
 * International database with facilities to specifie exhange markets and new indicators from zipline, portfolio table, cleaning shiny, some cool tools, moved network configuration in config dir, new backtest initialization (bis)
 * International database with facilities to specifie exhange markets and new indicators from zipline, portfolio table, cleaning shiny, some cool tools, moved network configuration in config dir, new backtest initialization
 * licenced, installation tested, clean, fixed, ready !
 * reshapes and bug fixes bedore dev meeting
 * reshapes, setup process, base of documentation
 * curses for remote console, interface for remote console, fixed some bugs
 * still intermediate clean (fixed)
 * still intermediate clean
 * distributed access and optimization algo
 * fixed format error
 * Intermediate cleaning, added comments, descriptions and removed some ugly or deprecated code
 * began genetic optimization process, communication architecture with generic distributed forwarder and android push notification
 * reshapes and new names
 * d3 and interprocess learning, 0MQ integration, some clean, some reshapes
 * live trade improvements and some more network play
 * first live test, manager factorisation, network tests
 * Some reshapes and every algos functionnal
 * shiny and algos update, manager bugs fixed
 * MySQL migration continued, portfolio strategie choice added, clean reports of backtest
 * MySQL integration in R scripts, as well as portfolio strategies entry points
 * Poco class removed, pnl and ui intro, some reshapes and a new master script in python
 * global runnner script and poco class, and new sql database implementation
 * Portfolio optimization added, backtest chain complete for 2 algos
 * Fork of zipline, notes.txt with open-source projects forks, backtester integration with quantopian algos
 * Bactest v1 with shiny version achieved
 * node.js server, rshiny improvements
 * csv file access, reshapes of getData, Network app (shiny+ server python), first forecasts (R arma+garch and svm
 * refactorisation and tests creation
 * Genetic optimization, backtesting integration and reshapes
 * Reorganization and first backtester implementation
 * SQLite interface usuable, uniform getData written by merging local db and network access
 * still many reshapes and little integration, graph subsystem added, new sqlite handler
 * some reshapes and new python utilities
 * Big dataAccess update and still a lot of work in playground. Dicvering qstk and quantopia
 * Big sandbox. Mainly integration of python and R wrapper, and new use of pandas or other python libs
 * Some more changes
 * old python downloader updated and added in the new version
 * New architecture version, powered by poco
 * dependencies fixed
 * test
 * branch test
 * Last basic functions added
 * Databases and their access ok
 * Global architecture functionnal
 * CLeaning up ! Many modifications yet
 * Clean
 * Some adds on new dir
 * New downloader and sqlite database
 * First structure version functionnal
 * [13-06-2012] Initial commit
 * [13-06-2012] Commit test

30-05-2013
----------
- Scripts to quickly begin a new strategie
- Quandl integration in datafeed
- New source selection available from command line
- New datasources
- Algos, managers and sources all stored in library file
- First minizipline script for quick and dirty tests

13-05-2013
----------
- Installation process improvement
- New GMV portfolio, optimal frontier cleaning
- tmpdata improvements
- POO Grid, monitoring and logs integration
- Algos and managers fixes
- Multi nodes deployment

23-04-2013
----------
- Errors module
- Many many fixes
- New RESTful API along of the broker
- Better live integration, with team_dashboard integration
- Grid deployement script

10-04-2013
----------
- Fixed run_app script for use on server
- New algorithms
- playground/webfrontend
- Tests and playground adds

02-04-2013
----------
- Quandl R and python implementation
- That + NotifyMyAndroid configs moved to default.json
- Database cli arument is now also an indicator to save or not results
- A quick and dirty menu for scripts/run_app.sh, along with my aliases
- Change file doublon to symbolic links
- Complete node server module, used in application directory
- Portfolio manager no longer needed
- Manual setup fixed


22-03-2013
----------
- UML and Presentation of the project in management/Introduction (french)
- Fixed new configuration reader bugs
- Began data module reshape (check in ziplinesource and tmpdata)
- Optimization module updated with new improvements
- New util and decorator functions
- Studies about bluetooth serial communication (smartphone client)
- start and end date specified with minute resolution and various format on command line (use of dateutil.parser.parse())
- Fixed live sources
- Generic timer and date handler for live sources
- Node server bug fixed
- Complete command line implementation in remote console
- On-the-fly orders
- Squizzing of the exception at the end of a very short live session in zipline
- Quick and dirty solution for dates timezone
- Android notififations OK
- Renames, splitted strategies and managers in different directories and files
- Fixed sharpe ratio computation


19-03-2013
----------
- Creating refactoring branch, much cleaner and up-to-date
- config.cfg file in *.json
- New configuration object
- New simulation configuration, with above object
- New Analyses class to handle backtests results
- Zipline: if live running, risk analysis get benchmark value running new function that downloads it
- Some improvements and fixes
- Converter bash script
- Use of pip-tools (https://github.com/nvie/pip-tools)
- Working sentiment analysis based on txt file with ranked words (multi-language !)
- Added UML file in neuronquant/management
- Instead of direct call in Simulation to SimulationParamaters, use zipline.utils.factory.create_simulation_parameters


15-03-2013
----------
- Forex realtime free access with R (through TrueFX)
- New database schema (Forex, IdxQuote, Equities + Indices = ex-Symbols)
- Python port of R TFX package
- Added stream_source field in data sent to live source to choose it
- Market hours filter in datautils
- New load_market_data function (class actually) for benchmark live update + integration in engine.py
- Renamed calculus in gears
- Database module fixes
- More robust yahoofinance, with an extra get_indice function
- Merged default.json and mysql.cfg configuration file and move it (with local.sh and shiny-server.config) to ~/.quantrade to fix password issue
- Installation script
- Many new ressources on project board


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
