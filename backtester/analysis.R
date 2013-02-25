#!/usr/bin/env Rscript

# file of analysis functions
source(paste(Sys.getenv('QTRADE'), 'server/shiny-backtest/global.R', sep='/'))

## ==========================    Args handle    =========================== ##
if(!suppressPackageStartupMessages(require(optparse)))
    stop('The optparse package is required to use the command line interface.')

option_list <- list( 
    make_option(c("-v", "--version"), 
        action = "store_true", default = FALSE,
        help   = "Print version info and exit"),
    make_option(c("-m", "--mode"), 
        action = "store_true", default = "regular",
        type   = "character", help     = "Specified wether it musts run experimental or regular analysis"),
    make_option(c("-d", "--db-location"), 
        action = "store_true", default = "../../metricsbase/stocks.db",
        type   = "character" ,help     = "SQLite metricsbase location")
    )

opt <- parse_args(OptionParser(option_list=option_list, usage="./script [options] <args>"))

## =========================    Preparing metrics    ========================== ##

metrics   <- getTradeData(dataId='test', source='mysql', debug=F)
perfs     <- getTradeData(dataId='test', source='mysql', overall=T, debug=F)
riskfree  <- mean(metrics[,"TreasuryReturns"])
portfolio <- metrics[, 'Returns']
benchmark <- metrics[, 'BenchmarkReturns']

## =========================       Analysis       ========================== ##

# General statistic observations
t(table.Stats(portfolio))
t(table.CAPM(portfolio, benchmark, Rf=riskfree, scale=12))
t(table.AnnualizedReturns(metrics[,c('Returns', 'BenchmarkReturns')], Rf=riskfree))

# Main graph for cummulative returns vizu
charts.PerformanceSummary(metrics[, c('Returns', 'BenchmarkReturns')], colorset=rich6equal)

# Together for performance enhancement
chart.RollingPerformance(portfolio, width = 12)

# Alpha, Beta, R-Squared
charts.RollingRegression(metrics[, 'Returns', drop=F], metrics[, 'BenchmarkReturns', drop=F])
# Rolling returns vs risks observation
chart.SnailTrail(metrics[, c('Returns')], Rf=riskfree)
t(table.DownsideRisk(portfolio))

# Distribution description
drawDistribution(metrics[, c('Returns', 'BenchmarkReturns')])

# Correlation to market
table.Correlation(portfolio, benchmark)
drawRelations(metrics[, c('Returns', 'BenchmarkReturns')])
chart.Correlation(metrics[, c('Returns', 'BenchmarkReturns')])
chart.Regression(metrics[, 'Returns', drop=F], metrics[, 'BenchmarkReturns', drop=F], Rf=riskfree, excess.returns=T, fit=c("loess", "linear"), legend.loc="topleft")

## ============================    Cleaning    ============================= ##
quit(save="no", status=0)

#NOTE A graph to show portfolio weights through time
#help(chart.StackedBar)
