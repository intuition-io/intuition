if (!suppressPackageStartupMessages(require(RMySQL))) {
    stop('This app needs sqlite database access. To install it, run "install.packages("RMySQL")".)')
}

if (!suppressPackageStartupMessages(require(RJSONIO))) {
    stop('This app needs to read json config file. To install it, run "install.packages("RJSONIO")".)')
}

if (!suppressPackageStartupMessages(require(RSQLite))) {
    stop('This app needs sqlite database access. To install it, run "install.packages("RSQLite")".)')
}

if (!suppressPackageStartupMessages(require(PerformanceAnalytics))) {
    stop("This app requires the PerformanceAnalytics package. To install it, run 'install.packages(\"PerformanceAnalytics\")'.\n")
}

if (!suppressPackageStartupMessages(require(quantmod))) {
    stop("This app requires the quantmod package. To install it, run 'install.packages(\"quantmod\")'.\n")
}

if (!suppressPackageStartupMessages(require(futile.logger))) {
    stop("This app requires the futile.logger package. To install it, run 'install.packages(\"futile.logger\")'.\n")
}

# This file defined json network bridge with R
source(paste(Sys.getenv('QTRADE'), 'application/shiny-backtest/RClientInterface.R', sep='/'))

# Util function
loadSilentely <- function(package)
{
    if (!suppressPackageStartupMessages(require(package))) {
        stop("Package not available. Install it with 'install.packages(\"\")'.\n")
    }
}

# Fix a bug in performanceanalytics package
require(utils)
assignInNamespace(
  "Return.excess",
  function (R, Rf = 0)
  { # @author Peter Carl
    # edited by orizon
      # .. additional comments removed
      R = checkData(R)
      if(!is.null(dim(Rf))){
          Rf = checkData(Rf)
          indexseries=index(cbind(R,Rf))
          columnname.Rf=colnames(Rf)
      }
      else {
          indexseries=index(R)
          columnname.Rf=Rf
          Rf=xts(rep(Rf, length(indexseries)),order.by=indexseries)
      }
      return.excess <- function (R,Rf)
      { 
          xR = coredata(as.xts(R))-coredata(as.xts(Rf)) #fixed
      }
      result = apply(R, MARGIN=2, FUN=return.excess, Rf=Rf)
      colnames(result) = paste(colnames(R), ">", columnname.Rf)
      result = reclass(result, R)
      return(result)
  },
  "PerformanceAnalytics"
)

getFromSQLite <- function(name='backtest', database='stocks.db', debug=FALSE)
{
    ## Data = c(strategie, peers, indexes)
    dbRoot <- Sys.getenv('QTRADEDATA')
    dbPath <- paste(dbRoot, database, sep="/")

    drv <- dbDriver("SQLite")
    flog.info('Connecting to database')
    connection <- dbConnect(drv, dbPath)
    ##TODO Checking the connection
    flog.debug('Check connection :')
    dbListTables(connection)
    if ( dbExistsTable(connection, name) ) {
        dbListFields(connection, name)

        flog.info('Table found, reading data...')
        ## Storing it in a dataframe and converting to xts object
        data <- dbReadTable(connection, name)
        ## Assuming dates are stored in last column, see python db
        datesIdx <- length(data)
        ## Old version: strategie <- as.xts(data[,-datesIdx], order.by=as.POSIXct(data[,datesIdx], origin="1970-01-01"))
        strategie <- xts(data[,-datesIdx], order.by=as.Date(data[,datesIdx]))
    } else {
        msg <- paste('** Error: No table named ', name)
        stop(msg)
    }

    if (debug)
    {
        flog.info('Some informations to check')
        head(strategie)
        colnames(strategie)
        periodicity(strategie)
        summary(strategie)
    }
    dbDisconnect(connection)
    dbUnloadDriver(drv)
    return(strategie)
}

# Access to backtest perfs stored in MySQL database
getMetricsFromMySQL <- function(dataId,                   # Table the backtest saved metrics
                                dbfile  = 'default.json', # Json mysql configuration file
                                overall = FALSE,          # When True, get final perfs, monthly otherwise
                                debug   = FALSE)
{
    # Getting database user settings
    #config <- fromJSON(file(paste(Sys.getenv('QTRADE'), 'config', dbfile, sep='/'), 'r'))['mysql'][[1]]
    config <- fromJSON(file(paste(Sys.getenv('HOME'),'.quantrade', 'config', dbfile, sep='/'), 'r'))['mysql'][[1]]

    db = dbConnect(MySQL(),
                   user     = config['user'][[1]],
                   password = config['password'][[1]],
                   dbname   = config['database'][[1]],
                   host     = config['hostname'][[1]])
    on.exit(dbDisconnect(db))

    # Choosing between final backtest analysis, or monthly perfs
	if ( overall ) 
	{
		table <- 'Performances'
	} else {
		table <- 'Metrics'
	}

    # Getting data
    stmt <- paste("SELECT * FROM ", table, " WHERE Name='", dataId, "'", sep="")
    rs = dbSendQuery(db, stmt)
    input <- fetch(rs, -1)
    if (debug)
    {
        flog.info(stmt)
        head(input)
        summary(input)
    }
    # monthly perfs are time series, casting it in suitable type data: xts
    if ( !overall && length(input) != 0)
        input =  xts(subset(input, select=-c(Name, Period, Id)), order.by=as.Date(input$Period))

	return(input)
}

#TODO Add dates selection
# Common interface to access data
getTradeData <- function(dataId   = 'backtest',       # Table to access
                         source   = 'mysql',          # Type of data store
                         config   = 'default.json',   # MySQL configuraiotn file
                         database = 'stocks.db',      # SQLite database name
                         overall  = FALSE,            # Final or monthly perfs
                         debug    = FALSE)
{
    if (source == 'sqlite')
    {
        perfs <- getFromSQLite(dataId, database, debug)
    }

    else if (source == 'mysql')
    {
        perfs <- getMetricsFromMySQL(dataId=dataId, dbfile=config, overall=overall, debug=debug)
    }

    if (debug)
    {
        head(perfs)
        #TODO Now with a logger library use debug flag for flog.threshold function
        flog.info('...')
        tail(perfs)
    }
    return(perfs)
}

drawDistribution <- function(returns) 
{
	portfolio = returns[, 'Returns', drop=FALSE]
    benchmark = returns[, 'BenchmarkReturns', drop=FALSE]
    layout(rbind(c(1,2), c(3,4), c(5,6)))
    chart.Histogram(portfolio, main="Plain", methods = NULL)
    chart.Histogram(portfolio, main="Density", breaks=40, methods = c("add.density", "add.normal"))
    chart.Histogram(portfolio, main="Skew and Kurt", methods = c("add.centered", "add.rug"))
    chart.Histogram(portfolio, main="RiskMeasures", methods = c("add.risk"))
	chart.QQPlot(portfolio, main="RiskMeasures")
    chart.Boxplot(returns[, c(1, 2)])
}

drawRelations <- function(returns, riskfree=0.0)
{
    portfolio = returns[, 'Returns', drop=FALSE]
    benchmark = returns[, 'BenchmarkReturns', drop=FALSE]
    #layout(rbind(c(1,2), c(3,4)))    
	layout(rbind(1, 2)) 
	chart.RelativePerformance(portfolio, benchmark, main="Relative performance", xaxis=TRUE)
    chart.RollingCorrelation(portfolio, benchmark, main="Relative Correlation")
}

#Do not plot second serie
Distributions <- function(series) 
{
    par(oma = c(5,0,2,1), mar=c(0,0,0,3))
    layout(matrix(1:8, ncol=4, byrow=TRUE), widths=rep(c(.6,1,1,1),length(colnames(series))))
    chart.mins=min(series)
    chart.maxs=max(series)
    row.names = sapply(colnames(series), function(x) paste(strwrap(x,10), collapse = "\n"), USE.NAMES=FALSE)
    for(i in 1:length(colnames(series))){
        plot.new()
        text(x=1, y=0.5, adj=c(1,0.5), labels=row.names[i], cex=1.1)
        chart.Histogram(series[,i], main="", xlim=c(chart.mins, chart.maxs), breaks=seq(-0.15,0.10, by=0.01), show.outliers=TRUE, methods=c("add.normal"))
        abline(v=0, col="darkgray", lty=2)
        chart.QQPlot(series[,i], main="", pch="*", envelope=0.95, col=c(1,"#005AFF"))
        abline(v=0, col="darkgray", lty=2)
        chart.ECDF(series[,i], main="", xlim=c(chart.mins, chart.maxs), lwd=2)
        abline(v=0, col="darkgray", lty=2)
    }
}

test <- function()
{
    perfs = getTradeData(dataId='backtest', source='mysql')
    ## ============================    Cleaning    ============================= ##
    quit(save="no", status=0)
}

# Some use 3months treasury bound
# It has to match the returns period
#riskfree <- .04/12  # My bank CD
#data <- NULL
data <- getTradeData(dataId='backtest', source='mysql', debug=TRUE)

#FIXME: NA
#riskfree <- mean(data[, 'TreasuryReturns'])
riskfree <- 0.4
