#suppressPackageStartupMessages(library("zoo"))
if (!require("RSQLite")) {
    stop('This app needs sqlite database access. To install it, run "install.packages("RSQLite")".)')
}

#if (!require(PerformanceAnalytics)) {
  #stop("This app requires the PerformanceAnalytics package. To install it, run 'install.packages(\"PerformanceAnalytics\")'.\n")
#}
#if (!require(quantmod)) {
  #stop("This app requires the quantmod package. To install it, run 'install.packages(\"quantmod\")'.\n")
#}


## =========================    Preparing data    ========================== ##
getTradeData <- function(name='test', database='stocks.db', debug=FALSE)
{
    ## Zoo.CalculateReturns()
    ## Data = c(strategkie, peers, indexes)
    #Using getwd() to handle from where it was ran ?
    #database <- '../../../Database/stocks.db'
    dbRoot <- Sys.getenv('QTRADEDATA')
    dbPath <- paste(dbRoot, database, sep="/")

    drv <- dbDriver("SQLite")
    connection <- dbConnect(drv, dbPath)
    ## Checking the connection
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

drawDistribution <- function(portfolio) 
{
    layout(rbind(c(1,2), c(3,4)))
    chart.Histogram(portfolio, main="Plain", methods = NULL)
    chart.Histogram(portfolio, main="Density", breaks=40, methods = c("add.density", "add.normal"))
    chart.Histogram(portfolio, main="Skew and Kurt", methods = c("add.centered", "add.rug"))
    chart.Histogram(portfolio, main="RiskMeasures", methods = c("add.risk"))
}

drawRelations <- function(returns)
{
    portfolio = returns[, 'algo_rets', drop=FALSE]
    benchmark = returns[, 'bench_rets', drop=FALSE]
    chart.RelativePerformance(portfolio, benchmark, main="Relative performance", xaxis=TRUE)
    chart.RollingCorrelation(portfolio, benchmark, main="Relative Correlation")
    chart.QQPlot(portfolio, main="RiskMeasures")
    chart.Boxplot(returns[, c(1, 2)])
}

test <- function()
{
    strategie = getTradeData(name='test')

    ## ===========================     Analysis     ============================= ##

    charts.PerformanceSummary(strategie[,c("algo_rets", "bench_rets")], colorset=rich6equal, main="Performance of the strategy")

    drawDistribution(strategie[, 'algo_rets'])

    #chart.RiskReturnScatter(strategie[, "algo_rets"], Rf = .03/12, main = "Annualized Return and Risk", add.names = TRUE, xlab = "Annualized Risk", ylab = "Annualized Return", 
                            #method = "calc", geometric = TRUE, scale = NA, add.sharpe = c(1, 2, 3), add.boxplots = TRUE, colorset = 1, symbolset = 1, element.color = "darkgray")
    #charts.RollingPerformance(strategie[, c("algo_rets", "bench_rets")])
    #charts.RollingRegression(strategie[, "algo_rets"], strategie[, "bench_rets"], Rf = 1.86, main = "Rolling Month CAPM analysis", envent.labels=TRUE)
    drawRelations(strategie[, c('algo_rets', 'bench_rets')])


    table.CalendarReturns(strategie[, c("algo_rets", "bench_rets")], digit=2)
    table.Stats(strategie[, "algo_rets"])
    table.Correlation(strategie[, "algo_rets"], strategie[, "bench_rets", drop=FALSE], legend.loc="lowerleft")
    #table.CPAM(strategie[trailing36.rows, "algo_rets"], strategie[trailing36.rows, "bench_rets", drop=FALSE], Rf=strategie[trailing36.rows, "risk_free", drop=FALSE])
    #table.CAPM(strategie[, "algo_rets"], strategie[, "bench_rets", drop=FALSE])
    table.DownsideRisk(strategie[, "algo_rets"], Rf=.03/12)
    table.Drawdowns(strategie[, "algo_rets", drop=F])

    ## ============================    Cleaning    ============================= ##
    quit(save="no", status=0)
}

