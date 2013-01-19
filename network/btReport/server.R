if (!require(PerformanceAnalytics)) {
    stop("This app requires the PerformanceAnalytics package. To install it, run 'install.packages(\"PerformanceAnalytics\")'.\n")
}

if (!require(quantmod)) {
    stop("This app requires the quantmod package. To install it, run 'install.packages(\"quantmod\")'.\n")
}

library(shiny)


source('../clientInterface.R')
source('bt_analyser.R')


# Download data for a stock, if needed
remoteExecute  <- function(cmd, host='localhost', port=2000)
{
    #FIXME First run quit annying
    cmds = unlist(strsplit(cmd, ' '))
    socket  <- make.socket(host, port)
    on.exit(close.socket(socket))
    output  <- read.socket(socket)
    answer <- remoteCmd(socket, 'state', print=FALSE)
    answer <- remoteJsonCmd(socket, 'user', cmd, print=FALSE)
    close.socket(socket)
}


# Define server logic required to summarize and view the selected dataset
shinyServer(function(input, output) 
{
    # Generate a plot of the system and buy/hold benchmark given nmonths parameter
    # include outliers if requested
    output$performance <- reactivePlot(function() 
    {
        data <- getTradeData(name='test')
        charts.PerformanceSummary(data[, c('algo_rets', 'bench_rets')], colorset=rich6equal, main='Performance of the strategie')
    })

    output$distribution <- reactivePlot(function() 
    {
        data <- getTradeData(name='test')
        drawDistribution(data[, 'algo_rets'])
    })

    output$relations <- reactivePlot(function() 
    {
        data <- getTradeData(name='test')
        drawRelations(data[, c('algo_rets', 'bench_rets' )])
    })

    # Generate a summary stats table of the dataset
    output$stats <- reactiveTable(function() 
    {
        data <- getTradeData(name='test')
        t(table.Stats(data[, 'algo_rets']))
    })

    output$drawdown <- reactiveTable(function()
    {
        data <- getTradeData(name='test')
        #table.DownsideRisk(data[, 'algo_rets'], Rf=.03/12)
        #table.Drawdowns(data[, 'algo_rets', drop=F])
        #table.CalendarReturns(data[, c('algo_rets', 'bench_rets')], digit=2)
        t(table.DownsideRisk(data[, 'algo_rets'], Rf=1.86))
    })

    output$correlation <- reactiveTable(function() 
    {
        data <- getTradeData(name='test')
        table.Correlation(data[, 'algo_rets'], data[, 'bench_rets'], legend.loc='lowerleft')
    })

    output$request <- reactivePrint(function() 
    {
        arguments <- list(ticker   = list(prefix = '--ticker'    , value = input$ticker),
                         algorithm = list(prefix = '--algorithm' , value = input$strategie),
                         delta     = list(prefix = '--delta'     , value = 1),
                         start     = list(prefix = '--start'     , value = paste('30/1/', min(input$dateSlider), sep='')),
                         end       = list(prefix = '--end'       , value = paste('30/7/', max(input$dateSlider), sep='')))
                         
        configuration <- list(short_window  = round(input$shortW * input$longW),
                       long_window   = input$longW,
                       buy_on_event  = 120,
                       sell_on_event = 80)

        request <- list(command   = 'run',
                       script     = 'pocoVersion/backtester/backtest.py',
                       monitoring = 0,
                       args       = arguments,
                       config     = configuration)
        remoteNodeWorker(request, port=8124, print=T)
    })
})
