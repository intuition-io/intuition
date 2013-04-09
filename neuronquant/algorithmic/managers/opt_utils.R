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

#TODO move later utils function like mysql access in a didicated module (or somewhat common in R package design)

# From http://statsadventure.blogspot.fr
#TODO - transaction costs, turnover constraints

suppressPackageStartupMessages(require(polynom))
suppressPackageStartupMessages(require(fImport))
suppressPackageStartupMessages(require(PerformanceAnalytics))
suppressPackageStartupMessages(require(tseries))
suppressPackageStartupMessages(require(stats))
suppressPackageStartupMessages(require(RMySQL))
suppressPackageStartupMessages(require(zoo))
suppressPackageStartupMessages(require(futile.logger))
suppressPackageStartupMessages(require(RJSONIO))

# Initial setup
options(scipen=100)
options(digits=4)
flog.threshold(INFO)


# Intermediate function used in portfolio rebalancing
reweight = function(returns, startWeight){
    flog.info('Re-computating weights')
    n          = nrow(returns)
    lastWeight = as.vector(startWeight)
    outReturn  = data.frame()
     
    for(i in seq(1,n)){
        rts        = as.vector(exp(returns[i,]))
        w          = lastWeight * rts
        sumW       = sum(w)
        w          = w / sumW

        r          = as.matrix(returns[i,]) %*% w

        lastWeight = w

        outReturn  = rbind(outReturn, r)
    }
    return (outReturn)
}

# Fetch from the net and return a shaped cumulative returns from it
downloadOneSerie = function (symbol, from, to) {
    # Read data from Yahoo! Finance
    flog.info('Downloading quotes %s fron yahoo! finance, from %s to %s.', symbol, from, to)
    input       = yahooSeries(symbol, from        = from, to = to)

    # Character Strings for Column Names
    adjClose    = paste(symbol, ".Adj.Close", sep = "")
    inputReturn = paste(symbol, ".Return", sep    = "")
    CReturn     = paste(symbol, ".CReturn", sep   = "")
    
    # Calculate the Returns and put it on the time series
    input.Return = returns(input[, adjClose])
    colnames(input.Return)[1] = inputReturn
    input = merge(input,input.Return)
    
    #Calculate the cumulative return and put it on the time series
    flog.info('Computing cumulative returns')
    input.first   = input[, adjClose][1]
    input.CReturn = fapply(input[,adjClose],FUN = function(x) log(x) - log(input.first))
    colnames(input.CReturn)[1] = CReturn
    input = merge(input,input.CReturn)
    
    #Deleting things (not sure I need to do this, but I can't not delete things if
    # given a way to...
    flog.debug('Cleaning temporary columns')
    rm(input.first,input.Return,input.CReturn,adjClose,inputReturn,CReturn)
    
    #Return the timeseries
    return(input)
}

## Do the same as above, but from sql database
serieFromDB <- function(symbol,
                        from,
                        to,                     #TODO default to today
                        dbfile='default.json')
{

    flog.info('Fetching serie from database')
    flog.info('Reading MySQL configuration')
    config <- fromJSON(file(paste('~/.quantrade', dbfile, sep='/'), 'r'))$mysql

    flog.debug('Connecting to MySQL')
    stocksDB = dbConnect(MySQL(),
                         user=config['user'][[1]], 
                         password=config['password'][[1]], 
                         dbname=config['database'][[1]], 
                         host=config['hostname'][[1]])
    on.exit(dbDisconnect(stocksDB))

    stmt <- paste("select Date, AdjClose from Quotes where Quotes.Ticker = ", symbol, " and Quotes.Date >= ", from, " and Quotes.Date <= ", to, "", sep="'") 
    flog.info('Execute: %s', stmt)
    rs = dbSendQuery(stocksDB, stmt)
    inputTmp = fetch(rs, -1)
    input <- xts(inputTmp['AdjClose'], order.by=as.Date(inputTmp$Date))

    # Character Strings for Column Names
    adjClose    = paste(symbol, ".Adj.Close", sep = "")
    inputReturn = paste(symbol, ".Return", sep    = "")
    CReturn     = paste(symbol, ".CReturn", sep   = "")

    # Calculate the Returns and put it on the time series
    input.Return    = xts(returns(input), order.by=as.Date(inputTmp$Date))
    input           = merge(input, input.Return)
    colnames(input) = c(adjClose, inputReturn)

    #Calculate the cumulative return and put it on the time series
    flog.info('Computing cumulative return')
    input.first                = input[, adjClose][1]
    input.CReturn              = fapply(timeSeries(input[,adjClose]), FUN = function(x) log(x) - log(input.first[[1]]))
    colnames(input.CReturn)[1] = CReturn
    input                      = merge(input,input.CReturn)

    rm(input.first, input.Return, input.CReturn, adjClose, inputReturn, CReturn, inputTmp)

    if (dbHasCompleted(rs))
    {
        dbClearResult(rs)
    }
    return(input)
}

# Main entry for data access
importSeries <- function(symbols,
                         from, 
                         to, 
                         source='yahoo')
{
    merged <- NULL
    for(sym in symbols)
    {
        flog.info('Fetching %s from %s', sym, source)
        if (source == 'yahoo')
        {
            # Remote access to quotes, provided by yahoo! finance
            returns = downloadOneSerie(sym, from, to)
        }
        else if (source == 'mysql')
        {
            returns = serieFromDB(sym, from, to)
        }
        # Merging with previous downloads
        if (!is.null(merged))
            merged = merge(merged, returns)
        else
            merged = returns
    }
    flog.info('Got data')
    return(merged)
}

#TODO Instead or 'error in this try', count errors and print a bilan
getEfficientFrontier <- function(returns, returnNames, periods=255, points=500, maxWeight=.334, Debug=FALSE, graph=FALSE)
{
    #create an empty data frame for the portfolio weights
    weights = data.frame(t(rep(NA,length(returnNames))))
    colnames(weights) = returnNames
    weights = weights[-1,]

    #Calculate Annualized Returns
    t = table.AnnualizedReturns(returns[,returnNames])

    #Range to optimize over
    maxRet = max(t['Annualized Return',]) - .005
    minRet = min(t['Annualized Return',]) + .005
    #set the max and min for the returns limit to 50% and the lower to .005%
    maxRet = min(.5,maxRet)
    minRet = max(0.005,minRet)

    #if all series have negative expected return, then only find the portfolio with the max return
    if (maxRet < 0){
        minRet = maxRet
        points = 1
    }
    #Debugging Print
    if (Debug){
        print("Max Return")
        print(maxRet)
        print("Min Return")
        print(minRet)
    }

    #portfolio.optim cannot have NA values in the time series, filter them out
    m2 = removeNA(returns[,returnNames])
    er = NULL
    eStd = NULL

    #loop through finding the optimum portfolio for return levels between the range found above
    #portfolio.optim uses daily returns, so we have to adjust accordingly
    ok = FALSE
    for (i in seq(minRet, maxRet, length.out=points)){
        pm = 1+i
        pm = log(pm) / periods
        if (Debug){
            print("Finding Optimum for")
            print("ER")
            print(pm)
            print(exp(pm * periods) - 1)
        }
        #optimization. limit weights to <= maxWeight
        #surround in tryCatch to catch unobtainable values
        opt = tryCatch(portfolio.optim(m2,
                                       pm=pm),
                                       #reshigh=rep(maxWeight,length(returnNames)),
                                       #shorts = FALSE),
                       error=function(err) return(NULL))

        #check to see if feasible solution exists
        if (!is.null(opt)){
            er = c(er, exp(pm * periods) - 1)
            eStd = c(eStd, opt$ps * sqrt(periods))
            w = t(opt$pw)
            colnames(w) = returnNames
            weights = rbind(weights, w)
            #update the OK variable
            ok = (ok | TRUE)
        } else {
            #print("** Error in this try")
            #update the OK variable
            ok = (ok | FALSE)
        }
    }
    #if no feasible solutions were found for the frontier, return NULL
    if (!ok){
        print('! No feasible solutions found for the frontier')
        return (NULL)
    }
    solution      = weights
    solution$er   = er
    solution$eStd = eStd
    if (graph)
    {
        plot(eStd^2, er, col='blue')
        legend(.014, 0.015, 'Efficient frontier', col='red', lty=c(1,1))
    }
    return(solution)
}

#TODO A correctif is needed, see posts and reweight
marketPortfolio = function(solution,
                           rf,
                           graph=FALSE,
                           points=500,
                           Debug=FALSE)
{
    #find the index values for the minimum Std and the max Er
    minIdx = which(solution$eStd == min(solution$eStd))
    maxIdx = which(solution$er == max(solution$er))
    if (Debug){
        print(minIdx)
        print(maxIdx)
    }
    subset = solution[minIdx:maxIdx,c("er","eStd")]
    subset$nAbove = NA

    #for each value in the subset, count the number of points
    #that lay below a line drawn through the point and the RF asset
    for (i in seq(1,maxIdx-minIdx+1)){
        toFit              = data.frame(er=rf, eStd=0)
        toFit              = rbind(toFit,subset[i,c("er","eStd")])
        fit                = lm(toFit$er ~ toFit$eStd)
        poly               = polynomial(coef=fit$coefficients)
        toPred             = subset
        colnames(toPred)   = c("actEr","eStd")
        toPred$er          = predict(poly,toPred[,"eStd"])
        toPred$diff        = toPred$er - toPred$actEr
        subset[i,"nAbove"] = nrow(toPred[which(toPred$diff > 0),])
    }

    #get the point of tangency -- where the number of points
    #below the line is maximized
    max  = max(subset$nAbove)
    er   = subset[which(subset$nAbove == max),"er"]
    eStd = subset[which(subset$nAbove == max),"eStd"]
    #if more than one portfolio is found, return the first
    if (length(er) > 1){
        er   = er[1]
        eStd = eStd[1]
    }
    #index of the market portfolio
    idx = which(solution$er == er & solution$eStd == eStd)
    if (Debug){
        print("solution")
        print(er)
        print(eStd)
        print(solution[idx,])
    }
    #Draw the line if requested
    if (graph){
        maxStd = max(solution$eStd) + .02
        maxRetg = max(solution$er) + .02
        plot(solution$eStd,
             solution$er,
             xlim=c(0,maxStd),
             ylim=c(0,maxRetg),
             ylab="Expected Yearly Return",
             xlab="Expected Yearly Std Dev",
             main="Efficient Frontier",
             col="red",
             type="l",
             lwd=2)
        abline(v=c(0), col="black", lty="dotted")
        abline(h=c(0), col ="black", lty="dotted")
        toFit = data.frame(er=rf,eStd=0)
        toFit = rbind(toFit,solution[idx,c("er","eStd")])
        fit = lm(toFit$er ~ toFit$eStd)
        abline(coef=fit$coefficients,col="blue",lwd=2)
    }
    #Return the market portfolio wieghts and eStd and eR
    out = solution[idx,]
    return (out)
}

usage <- function(symbols)
{
    from = "2005-01-01"
    to   = "2011-12-16"
    #returnNames = c("xom.Return","ibm.Return","ief.Return")

    data = importSeries(symbols, from, to, source='mysql')
    for (i in seq(length(symbols))) 
    { 
        symbols[i] = paste(symbols[i], '.Return', sep='')
    }


    # Period is the frequency over a year of the returns
    frontier <- getEfficientFrontier(data, symbols, points=500, Debug=T, graph=T)
    mp = marketPortfolio(frontier, .02, Debug=T, graph=T)
}

#usage(c('xom', 'ibm', 'ief'))
