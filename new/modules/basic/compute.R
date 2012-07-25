#!/usr/bin/env Rscript

library("zoo")
library("DBI")
library("Defaults")
library("xts")
library("TTR")
library("RSQLite")
require("quantmod")
library("RJSONIO")

## =========================    Preparing data    ========================== ##
source("./modules/basic/finance.R")

args <- commandArgs()
company <- args[4]
database <- "./assets.db"

config_f <- args[5]

config = ""
connection <- file(config_f, open='r')
while ( length(line <- readLines(connection, n=1, warn= FALSE)) > 0 ) {
    config <- paste(config, line)
}
parameters <- fromJSON(config)

drv <- dbDriver("SQLite")
connection <- dbConnect(drv, database)
## Checking the connection
#dbListTables(connection)
#dbListFields(connection, company)
## Storing it in a dataframe and converting to xts object
data <- dbReadTable(connection, company)
xts_data <- as.xts(data[,-1], order.by=as.POSIXct(data[,1], origin="1970-01-01"))
## ===============================    End    =============================== ##


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
## ===============================    End    =============================== ##


## ===============================   Plots   =============================== ##
trade_plot(xts_data, company, parameters$compute["macd"], "Calling trade_plot() function")
## ===============================    End    =============================== ##


## Sending query
field = "ma"
query <- "update"
#query <- paste(query, args[4])
query <- paste(query, "computations set")
query <- paste(query, field)
query <- paste(query, "=")
query <- paste(query, delta)
debug <- paste("[DEBUG] Updating database: ", query)
#print(debug[135])
#rs <- dbSendQuery(connection, query)
#data <- fetch(rs,n=3) #3 rows, -1 for all
#print(data)
#dbHasCompleted(rs)

## Cleaning up
#dbClearResult(rs)
dbDisconnect(connection)
dbUnloadDriver(drv)
