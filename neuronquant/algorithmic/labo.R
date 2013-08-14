#
# Copyright 2012 Xavier Bruhiere
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


suppressPackageStartupMessages(require(polynom))
suppressPackageStartupMessages(require(fImport))
suppressPackageStartupMessages(require(PerformanceAnalytics))
suppressPackageStartupMessages(require(tseries))
suppressPackageStartupMessages(require(stats))
suppressPackageStartupMessages(require(RMySQL))
suppressPackageStartupMessages(require(zoo))

options(scipen=100)
options(digits=4)

symbol = 'goog'
from = '2005-01-10'
to = '2010-01-10'

stocksDB = dbConnect(MySQL(), user='xavier', password='quantrade', dbname='stock_data', host='localhost')
#on.exit(dbDisconnect(stocksDB))
stmt <- paste("select Date, AdjClose from Quotes where Quotes.Ticker = ", symbol, " and Quotes.Date >= ", from, " and Quotes.Date <= ", to, "", sep="'") 
print(stmt)
rs = dbSendQuery(stocksDB, stmt)
inputTmp = fetch(rs, -1)
#input = data.frame(input['AdjClose'], row.names=input$Date)
input <- xts(inputTmp['AdjClose'], order.by=as.Date(inputTmp$Date))
#index(input) <- as.Date(inputTmp$Date)

# Character Strings for Column Names
adjClose    = paste(symbol, ".Adj.Close", sep = "")
inputReturn = paste(symbol, ".Return", sep    = "")
CReturn     = paste(symbol, ".CReturn", sep   = "")

# Calculate the Returns and put it on the time series
input.Return    = xts(returns(input), order.by=as.Date(inputTmp$Date))
input           = merge(input, input.Return)
colnames(input) = c(adjClose, inputReturn)

#Calculate the cumulative return and put it on the time series
input.first                = input[, adjClose][1]
input.CReturn              = fapply(timeSeries(input[,adjClose]), FUN = function(x) log(x) - log(input.first[[1]]))
colnames(input.CReturn)[1] = CReturn
input                      = merge(input,input.CReturn)

#Deleting things (not sure I need to do this, but I can't not delete things if
# given a way to...
rm(input.first, input.Return, input.CReturn, input.AdjClose, adjClose, inputReturn, CReturn)

if (dbHasCompleted(rs))
{
    dbClearResult(rs)
}
