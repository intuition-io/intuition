# Define server logic required to summarize and view the selected dataset

#FIXME Each change make the server to re-read the database (or data)
shinyServer(function(input, output) 
{
    #TODO parameters hard coded ! Re-think this part
    compute <- reactive(function() 
    {
        arguments <- list(ticker   = list(prefix = '--ticker'    , value = input$ticker),
                         algorithm = list(prefix = '--algorithm' , value = input$strategie),
                         delta     = list(prefix = '--delta'     , value = 1),
                         manager   = list(prefix = '--manager'   , value = input$manager),
                         mode      = list(prefix = 'flag'        , value = '--remote'),
                         start     = list(prefix = '--start'     , value = paste(min(input$dateSlider), '-10-01', sep='')),
                         end       = list(prefix = '--end'       , value = paste(max(input$dateSlider), '-10-07', sep='')))
                         
        if (input$strategie == 'DualMA')
        {
            algo <- list(short_window     = round(input$shortW * input$longW),
                              long_window = input$longW,
                              threshold   = input$threshold,
                              debug       = input$debug)
        }
        else if (input$strategie == 'Momentum') 
        {
            algo <- list(debug = input$debug,
                              window_length = input$window)
        }
        else (input$strategie == 'BuyAndHold') 
        {
            algo <- list(debug = input$debug)
        }

        portfolio <- list(loopback    = input$loopback,
                        source      = input$source,
                        max_weight  = 0.5,
                        connected   = 0,
                        buy_amount  = 200,
                        sell_amount = 100)

        config <- list(algorithm = algo,
                       manager   = portfolio)

        request <- list(type          = 'fork',
                        script        = 'application/app.py',
                        port          = 5555,
                        monitoring    = 0,
                        args          = arguments,
                        configuration = config)
        
        if ( input$done )
        {
            #remoteNodeWorker(request, port=5555, debug=F)
            zmqSend(request, config='default.json', debug=TRUE)
        } 
        getTradeData(dataId=input$dataTable, config='default.json', source='mysql')
    })

    output$performance <- renderPlot(function() 
    {
        charts.PerformanceSummary(compute()[, c('Returns', 'BenchmarkReturns')], colorset=rich6equal, main='Performance of the strategie')
    })

    output$distribution <- renderPlot(function() 
    {
        drawDistribution(compute()[, c('Returns', 'BenchmarkReturns')])
    })

    output$relations <- renderPlot(function() 
    {
        drawRelations(compute()[, c('Returns', 'BenchmarkReturns' )], riskfree=riskfree)
    })

    output$rollperfs <- renderPlot(function() 
    {
        chart.RollingPerformance(compute()[, 'Returns'], width=12)
    })

    output$rollregression <- renderPlot(function() 
    {
        charts.RollingRegression(compute()[, 'Returns', drop=FALSE], compute()[, 'BenchmarkReturns', drop=FALSE])
    })

    output$regression <- renderPlot(function() 
    {
        chart.Regression(compute()[, 'Returns', drop=F], compute()[, 'BenchmarkReturns', drop=F], Rf=riskfree, excess.returns=T, fit=c('loess', 'linear'), legend.loc='topleft')
    })

    output$snailtrail <- renderPlot(function() 
    {
        chart.SnailTrail(compute()[, 'Returns'], Rf=riskfree)
    })

    output$plotcorr <- renderPlot(function() 
    {
        chart.Correlation(compute()[, c('Returns', 'BenchmarkReturns')])
    })

    ## Generate a summary stats table of the dataset
    output$stats <- renderTable(function() 
    {
        t(table.Stats(compute()[, 'Returns']))
    })

    output$drawdown <- renderTable(function()
    {
        t(table.DownsideRisk(compute()[, 'Returns'], Rf=riskfree))
    })

    output$correlation <- renderTable(function() 
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

    output$capm <- renderTable(function()
    {
        t(table.CAPM(compute()[, 'Returns'], compute()[, 'BenchmarkReturns'], Rf=riskfree, scale=12))
    })

    output$annualizedRets <- renderTable(function()
    {
        t(table.AnnualizedReturns(compute()[, c('Returns', 'BenchmarkReturns')], Rf=riskfree))
    })

})
