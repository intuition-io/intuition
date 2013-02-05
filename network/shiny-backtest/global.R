suppressPackageStartupMessages(require(RMySQL))
if (!suppressPackageStartupMessages(require("RSQLite"))) {
    stop('This app needs sqlite database access. To install it, run "install.packages("RSQLite")".)')
}

if (!suppressPackageStartupMessages(require(PerformanceAnalytics))) {
    stop("This app requires the PerformanceAnalytics package. To install it, run 'install.packages(\"PerformanceAnalytics\")'.\n")
}

if (!suppressPackageStartupMessages(require(quantmod))) {
    stop("This app requires the quantmod package. To install it, run 'install.packages(\"quantmod\")'.\n")
}

source('./RClientInterface.R')

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

getFromSQLite <- function(name='test', database='stocks.db', debug=FALSE)
{
    ## Data = c(strategie, peers, indexes)
    dbRoot <- Sys.getenv('QTRADEDATA')
    dbPath <- paste(dbRoot, database, sep="/")

    drv <- dbDriver("SQLite")
    connection <- dbConnect(drv, dbPath)
    ##TODO Checking the connection
    dbListTables(connection)
    if ( dbExistsTable(connection, name) ) {
        dbListFields(connection, name)

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
        print('Some informations to check')
        head(strategie)
        colnames(strategie)
        periodicity(strategie)
        summary(strategie)
    }
    dbDisconnect(connection)
    dbUnloadDriver(drv)
    return(strategie)
}

getMetricsFromMySQL <- function(dataId, dbname='stock_data', password='', user='xavier', host='localhost', overall=FALSE, debug=FALSE)
{
    db = dbConnect(MySQL(), user=user, password=password, dbname=dbname, host=host) 
    on.exit(dbDisconnect(db))
	if ( overall ) 
	{
		table <- 'Performances'
	} else {
		table <- 'Metrics'
	}
    stmt <- paste("SELECT * FROM ", table, " WHERE Name='", dataId, "'", sep="")
    rs = dbSendQuery(db, stmt)
    input <- fetch(rs, -1)
    if (debug)
    {
        print(stmt)
        head(input)
        summary(input)
    }
	if ( !overall )
    	input =  xts(subset(input, select=-c(Name, Period, Id)), order.by=as.Date(input$Period))
	return(input)
}

#TODO Add dates selection
getTradeData <- function(dataId='test', database='stocks.db', source='sqlite', overall=FALSE, debug=FALSE)
{
    if (source == 'sqlite')
    {
        perfs <- getFromSQLite(dataId, database, debug)
    }
    else if (source == 'mysql')
    {
        perfs <- getMetricsFromMySQL(dataId, password='quantrade', overall=overall, debug=debug)
    }
    if (debug)
    {
        head(perfs)
        print('...')
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
    perfs = getTradeData(dataId='test', source='mysql')
    ## ============================    Cleaning    ============================= ##
    quit(save="no", status=0)
}

# Some use 3months treasury bound
# It has to match the returns period
#Rf <- .04/12  # My bank CD
data <- getTradeData(dataId='test', source='mysql')
riskfree <- mean(data[, 'TreasuryReturns'])
#data <- NULL
