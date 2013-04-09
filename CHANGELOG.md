Changelog
=========

02-04-2013
----------
- Quandl R and python implementation
- That + NotifyMyAndroid configs moved to default.json
- Database cli arument is now also an indicator to save or not results
- A quick and dirty menu for scripts/run_app.sh, along with my aliases
- Change file doublon to symbolic links
- Complete node server module, used in application directory

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
