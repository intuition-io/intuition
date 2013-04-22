#!/usr/bin/env Rscript
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


# This script performs some quantitative analyzis on trade results
# stored in database

# file of analyzis functions
analyzisLib <- paste(Sys.getenv('QTRADE'),
                     'application/shiny-backtest/global.R',
                     sep='/')
source(analyzisLib)

## ==========================    Args handle    =========================== ##
if(!suppressPackageStartupMessages(require(optparse)))
    stop('The optparse package is required to use the command line interface. run install.packages("optparse").\n')

option_list <- list( 
    make_option(c("-v", "--verbose"), 
        action = "store_true", default = FALSE,
        help   = "Print extra output"),
    make_option(c("-s", "--source"), 
        action = "store_true", default = "mysql",
        type   = "character" ,help     = "Type of source where there is data to process"),
    make_option(c("-t", "--table"), 
        action = "store_true", default = "test",
        type   = "character" ,help     = "MySQL or SQLite database table to analyse")
    )

opt <- parse_args(OptionParser(option_list=option_list, usage="./script [options] <args>"))

## ========================    Preparing metrics    ======================= ##

# Retrieve from database monthly rolling metrics
metrics   <- getTradeData(dataId=opt$table, source=opt$source, debug=opt$verbose)

# Retrieve final performances summary
perfs     <- getTradeData(dataId=opt$table, source=opt$source, overall=T, debug=opt$verbose)

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
chart.Regression(metrics[, 'Returns', drop=F], metrics[, 'BenchmarkReturns', drop=F], Rf=riskfree,
                 excess.returns=T, fit=c("loess", "linear"), legend.loc="topleft")

## ============================    Cleaning    ============================= ##
quit(save="no", status=0)

#NOTE A graph to show portfolio weights through time
#help(chart.StackedBar)
