#!/usr/bin/env Rscript

library("zoo")
library("DBI")
library("Defaults")
library("xts")
library("TTR")
library("RSQLite")
#require("quantmod")
library("quantmod")
library("RJSONIO")

## =========================    Preparing data    ========================== ##

#args <- commandArgs()
args <- commandArgs(trailingOnly = TRUE)
print(args)
# trailingOnly=TRUE means that only arguments after --args are returned
# if trailingOnly=FALSE then you got:
# [1] "R -q --slave --no-restore --no-save --args example 100 < script.R
config_f <- args[4]
target <- args[5]
rm(args)
#config_f <- "./modules/basic/config.json"
#config_f <- "./config.json"
print(config_f)
print(target)

config = ""
connection <- file(config_f, open='r')
while ( length(line <- readLines(connection, n=1, warn= FALSE)) > 0 ) {
    config <- paste(config, line)
}
parameters <- fromJSON(config)
source(parameters["rmodule"])
database <- parameters["assetsdb"]
#target <- parameters["name"]
close(connection)

drv <- dbDriver("SQLite")
connection <- dbConnect(drv, database)
## Checking the connection
#dbListTables(connection)
#dbListFields(connection, target)
## Storing it in a dataframe and converting to xts object
data <- dbReadTable(connection, target)
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
trade_plot(xts_data, target, parameters["macd"], "Calling trade_plot() function")
## ===============================    End    =============================== ##


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

q(status=0)
