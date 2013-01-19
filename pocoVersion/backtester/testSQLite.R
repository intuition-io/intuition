#!/usr/bin/env Rscript

suppressPackageStartupMessages(library("zoo"))
library("DBI")
library("Defaults")
library("xts")
library("TTR")
library("RSQLite")

if (!require(PerformanceAnalytics)) {
  stop("This app requires the PerformanceAnalytics package. To install it, run 'install.packages(\"PerformanceAnalytics\")'.\n")
}
if (!require(quantmod)) {
  stop("This app requires the quantmod package. To install it, run 'install.packages(\"quantmod\")'.\n")
}
## ==========================    Args handle    =========================== ##
if(!suppressPackageStartupMessages(require(optparse)))
  stop('The optparse package is required to use the command line interface.')

option_list <- list( 
    make_option(c("-v", "--version"), 
        action="store_true", default=FALSE,
        help="Print version info and exit"),
    make_option(c("-t", "--target"), 
        action="store_true", default="test",
        type="character", help="Target asset to be processed"),
    make_option(c("-m", "--macd"), 
        action="store_true", default=FALSE,
        help="Macd flag, sent to plot subsystem"),
    make_option(c("-d", "--db-location"), 
        action="store_true", default="../../Database/stocks.db",
        type="character" ,help="SQLite database location")
    )

opt <- parse_args(OptionParser(option_list=option_list, 
    usage = "./script [options] <args>"))

## =========================    Preparing data    ========================== ##
#Using getwd() to handle from where it was ran ?
#TODO: modules loading
database <- opt[['db-location']]
target <- opt$target

drv <- dbDriver("SQLite")
connection <- dbConnect(drv, database)
## Checking the connection
dbListTables(connection)
if ( dbExistsTable(connection, target) ) {
    dbListFields(connection, target)

    ## Storing it in a dataframe and converting to xts object
    data <- dbReadTable(connection, target)
    ## Assuming dates are stored in last column, see python db
    datesIdx <- length(data)
    ## Old version: xtsData <- as.xts(data[,-datesIdx], order.by=as.POSIXct(data[,datesIdx], origin="1970-01-01"))
    xtsData <- xts(data[,-datesIdx], order.by=as.Date(data[,datesIdx]))
} else {
    msg <- paste('** Error: No table named ', target)
    stop(msg)
}


## ===========================    Some infos    ============================ ##
print("Some summary informations")
head(xtsData)
colnames(xtsData)
periodicity(xtsData)
last(xtsData$close)
summary(xtsData)

## ===========================     Analysis     ============================= ##
charts.PerformanceSummary(xtsData[,c("algo_rets", "bench_rets")], main="Performance of the strategy")
chart.Boxplot(xtsData[,c("algo_rets", "bench_rets")])

layout(rbind(c(1,2), c(3,4)))
chart.Histogram(xtsData[, "algo_rets"], main="Plain", methods = NULL)
chart.Histogram(xtsData[, "algo_rets"], main="Density", breaks=40, methods = c("add.density", "add.normal"))
chart.Histogram(xtsData[, "algo_rets"], main="Skew and Kurt", methods = c("add.centered", "add.rug"))
chart.Histogram(xtsData[, "algo_rets"], main="RiskMeasures", methods = c("add.risk"))

## ============================    Cleaning    ============================= ##
dbDisconnect(connection)
dbUnloadDriver(drv)
quit(save="no", status=0)
