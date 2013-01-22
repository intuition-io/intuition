# Define server logic required to summarize and view the selected dataset

shinyServer(function(input, output) 
{
    # Generate a plot of the system and buy/hold benchmark given nmonths parameter
    # include outliers if requested
    compute <- reactive(function() 
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
        if ( input$done )
        {
            remoteNodeWorker(request, port=8124, debug=F)
        } 
        getTradeData(name=input$dataTable)
    })

    output$performance <- reactivePlot(function() 
    {
        charts.PerformanceSummary(compute()[, c('algo_rets', 'bench_rets')], colorset=rich6equal, main='Performance of the strategie')
    })

    output$distribution <- reactivePlot(function() 
    {
        drawDistribution(compute()[, 'algo_rets'])
    })

    output$relations <- reactivePlot(function() 
    {
        drawRelations(compute()[, c('algo_rets', 'bench_rets' )])
    })

    ## Generate a summary stats table of the dataset
    output$stats <- reactiveTable(function() 
    {
        t(table.Stats(compute()[, 'algo_rets']))
    })

    output$drawdown <- reactiveTable(function()
    {
        #table.DownsideRisk(data[, 'algo_rets'], Rf=.03/12)
        #table.Drawdowns(data[, 'algo_rets', drop=F])
        #table.CalendarReturns(data[, c('algo_rets', 'bench_rets')], digit=2)
        t(table.DownsideRisk(compute()[, 'algo_rets'], Rf=1.86))
    })

    output$correlation <- reactiveTable(function() 
    {
        table.Correlation(compute()[, 'algo_rets'], compute()[, 'bench_rets'], legend.loc='lowerleft')
    })

    output$results <- reactivePrint(function()
    {
        summary(compute())
    })

    output$outhead <- reactivePrint(function()
    {
        tail(compute())
    })

})
