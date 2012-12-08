#!/usr/bin/env Rscript

suppressPackageStartupMessages(library("zoo"))
library("DBI")
library("Defaults")
library("xts")
library("TTR")
library("RSQLite")
library("quantmod")

## =========================    Preparing data    ========================== ##
if(!suppressPackageStartupMessages(require(optparse)))
  stop('The optparse package is required to use the command line interface to pgfSweave.')

option_list <- list( 
    make_option(c("-v", "--version"), 
        action="store_true", default=FALSE,
        help="Print version info and exit"),
    make_option(c("-t", "--target"), 
        action="store_true", default="google",
        type="character", help="Target asset to be processed"),
    make_option(c("-m", "--macd"), 
        action="store_true", default=FALSE,
        help="Macd flag, sent to plot subsystem"),
    make_option(c("-d", "--db-location"), 
        action="store_true", default="../dataSubSystem/assets.db",
        type="character" ,help="SQLite database location")
    )

opt <- parse_args(OptionParser(option_list=option_list, 
    usage = "./script [options] <args>"))

## =========================    Preparing data    ========================== ##
#Using getwd() to handle from where it was ran ?
#TODO: modules loading
source("../computeSubSystem/statistics.R")
source("../GUISubSystem/quantPlot.R")
database <- opt[['db-location']]
target <- opt$target
macd <- opt$macd

drv <- dbDriver("SQLite")
connection <- dbConnect(drv, database)
## Checking the connection
#dbListTables(connection)
#dbListFields(connection, target)

## Storing it in a dataframe and converting to xts object
data <- dbReadTable(connection, target)
xts_data <- as.xts(data[,-1], order.by=as.POSIXct(data[,1], origin="1970-01-01"))


## ===========================    Some infos    ============================ ##
print("Some summary informations")
periodicity(xts_data)
last(xts_data$close)
summary(xts_data$open)
summary(xts_data$volume)

## Exponential average and associated delta
ma97 = ema(data[, "close"])
ma94 = ema(data[, "close"], 0.94)
delta = ma94 - ma97


## ===============================   Plots   =============================== ##
trade_plot(xts_data, target, macd, "Calling trade_plot() function")


## ============================   Updating DB   ============================ ##
lastData = delta[length(delta)]
print(lastData)
## Sending query
table = "basic"
field = "ma"
query <- "update"
#query <- paste(query, args[4])
query <- paste(query, table)
query <- paste(query, "set")
query <- paste(query, field)
query <- paste(query, "=")
query <- paste(query, lastData)
debug <- paste("[DEBUG] Updating database: ", query)
print(debug)
rs <- dbSendQuery(connection, query)
#data <- fetch(rs,n=3) #3 rows, -1 for all
#dbHasCompleted(rs)

## Cleaning up
dbClearResult(rs)
dbDisconnect(connection)
dbUnloadDriver(drv)

quit(save="no", status=0)
