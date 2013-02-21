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
                         manager   = list(prefix = '--manager'   , value = input$manager),
                         start     = list(prefix = '--start'     , value = paste(min(input$dateSlider), '-10-01', sep='')),
                         end       = list(prefix = '--end'       , value = paste(max(input$dateSlider), '-10-07', sep='')))
                         
        if (input$strategie == 'DualMA')
        {
            algorithm <- list(short_window  = round(input$shortW * input$longW),
                              long_window   = input$longW,
                              threshold = input$threshold)
        }
        else if (input$strategie == 'Momentum') 
        {
            algorithm <- list(debug = input$debug,
                              window_length = input$window)
        }
        else (input$strategie == 'BuyAndHold') 
        {
            algorithm <- list(debug = input$debug)
        }

        manager <- list(loopback = input$loopback,
                        source   = input$source)

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
        getTradeData(dataId=input$dataTable, source='mysql')
    })

    output$performance <- reactivePlot(function() 
    {
        charts.PerformanceSummary(compute()[, c('Returns', 'BenchmarkReturns')], colorset=rich6equal, main='Performance of the strategie')
    })

    output$distribution <- reactivePlot(function() 
    {
        drawDistribution(compute()[, c('Returns', 'BenchmarkReturns')])
    })

    output$relations <- reactivePlot(function() 
    {
        drawRelations(compute()[, c('Returns', 'BenchmarkReturns' )], riskfree=riskfree)
    })

    output$rollperfs <- reactivePlot(function() 
    {
        chart.RollingPerformance(compute()[, 'Returns'], width=12)
    })

    output$rollregression <- reactivePlot(function() 
    {
        charts.RollingRegression(compute()[, 'Returns', drop=FALSE], compute()[, 'BenchmarkReturns', drop=FALSE])
    })

    output$regression <- reactivePlot(function() 
    {
        chart.Regression(compute()[, 'Returns', drop=F], compute()[, 'BenchmarkReturns', drop=F], Rf=riskfree, excess.returns=T, fit=c('loess', 'linear'), legend.loc='topleft')
    })

    output$snailtrail <- reactivePlot(function() 
    {
        chart.SnailTrail(compute()[, 'Returns'], Rf=riskfree)
    })

    output$plotcorr <- reactivePlot(function() 
    {
        chart.Correlation(compute()[, c('Returns', 'BenchmarkReturns')])
    })

    ## Generate a summary stats table of the dataset
    output$stats <- reactiveTable(function() 
    {
        t(table.Stats(compute()[, 'Returns']))
    })

    output$drawdown <- reactiveTable(function()
    {
        t(table.DownsideRisk(compute()[, 'Returns'], Rf=riskfree))
    })

    output$correlation <- reactiveTable(function() 
    {
        table.Correlation(compute()[, 'Returns'], compute()[, 'BenchmarkReturns'], legend.loc='lowerleft')
    })

    output$results <- reactivePrint(function()
    {
        summary(compute())
    })

    output$outhead <- reactivePrint(function()
    {
        tail(compute())
    })

    output$capm <- reactiveTable(function()
    {
        t(table.CAPM(compute()[, 'Returns'], compute()[, 'BenchmarkReturns'], Rf=riskfree, scale=12))
    })

    output$annualizedRets <- reactiveTable(function()
    {
        t(table.AnnualizedReturns(compute()[, c('Returns', 'BenchmarkReturns')], Rf=riskfree))
    })

})
