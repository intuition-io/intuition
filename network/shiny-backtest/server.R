# Define server logic required to summarize and view the selected dataset

#FIXME Each change make the server to re-read the database (or data)
shinyServer(function(input, output) 
{
    #NOTE parameters hard coded !
    compute <- reactive(function() 
    {
        arguments <- list(ticker   = list(prefix = '--ticker'    , value = input$ticker),
                         algorithm = list(prefix = '--algorithm' , value = input$strategie),
                         delta     = list(prefix = '--delta'     , value = 1),
                         manager   = list(prefix = '--manager'   , value = 'OptimalFrontier'),
                         start     = list(prefix = '--start'     , value = paste(min(input$dateSlider), '-10-01', sep='')),
                         end       = list(prefix = '--end'       , value = paste(max(input$dateSlider), '-10-07', sep='')))
                         
        algorithm <- list(short_window  = round(input$shortW * input$longW),
                          long_window   = input$longW,
                          buy_on_event  = 120,
                          sell_on_event = 80)

        manager <- list(loopback = 60,
                        source   = 'mysql')

        request <- list(command   = 'run',
                       script     = 'backtester/backtest.py',
                       monitoring = 0,
                       args       = arguments,
                       algo       = algorithm,
                       manager    = manager)
        
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
