#!/usr/bin/env Rscript

source('./global.R')

## ==========================    Args handle    =========================== ##
if(!suppressPackageStartupMessages(require(optparse)))
  stop('The optparse package is required to use the command line interface.')

option_list <- list( 
    make_option(c("-v", "--version"), 
        action="store_true", default=FALSE,
        help="Print version info and exit"),
    make_option(c("-m", "--mode"), 
        action="store_true", default="regular",
        type="character", help="Specified wether it musts run experimental or regular analysis"),
    make_option(c("-d", "--db-location"), 
        action="store_true", default="../../Database/stocks.db",
        type="character" ,help="SQLite database location")
    )

opt <- parse_args(OptionParser(option_list=option_list, 
    usage = "./script [options] <args>"))

## =========================    Preparing data    ========================== ##
data <- getTradeData(name='test')
head(data)

if (opt$mode == 'regular') 
{
    charts.PerformanceSummary(data[, c('algo_rets', 'bench_rets')])
    chart.RollingPerformance(data[, 'algo_rets'], width = 12)
    chart.RelativePerformance(data[, 'algo_rets'], data[, 'bench_rets'])
    #drawDistribution(data[, 'algo_rets'])
    chart.RollingCorrelation(data[, 'algo_rets'], data[, 'bench_rets'])
    t(table.Stats(data[, 'algo_rets']))
    t(table.CAPM(data[, 'algo_rets'], data[, 'bench_rets'], Rf=.04/12, scale=12))
} else{
    # A chart that shows rolling calculations of annualized return and
    # annualized standard deviation have proceeded through time.  Lines
    # and dots are darker for more recent time periods.
    chart.SnailTrail(data[, c('algo_rets')], Rf=1.86)
    chart.RiskReturnScatter(data[, c('algo_rets')], Rf=1.86)

    ## Rolling performance
    chart.RollingCorrelation(data[, 'algo_rets'], data[, 'bench_rets'])
    chart.Correlation(data[, c('algo_rets', 'bench_rets')])
    table.Correlation(data[, 'algo_rets'], data[, 'bench_rets'])

    chart.RollingPerformance(data[, 'algo_rets'], width = 6)

    ## Benchmark evaluation
    ## Does not work !
    charts.RollingRegression(data[, 'algo_rets', drop=F], data[, 'bench_rets', drop=F])
    chart.Regression(data[, 'algo_rets', drop=F], data[, 'bench_rets', drop=F], Rf=.04/12)

    # Autocorrellation
    chart.ACFplus(data[, 'algo_rets'])
    table.Autocorrelation(data[, 'algo_rets'])
}

## ============================    Cleaning    ============================= ##
quit(save="no", status=0)
