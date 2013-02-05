library(shiny)
 
# Define UI for dataset viewer application
shinyUI(pageWithSidebar(
    # Application title
    headerPanel("QuanTrade backtester front-end"),
  
    sidebarPanel(

        wellPanel(
            numericInput("amount", p(strong("Portfolio")), 10000),

            textInput("ticker", "Action", value="starbucks"),    

            textInput("dataTable", "Dataset", value="test"),    

            sliderInput(inputId = 'dateSlider', label = 'Period to trade',
                        min = 2000, max= 2012, value = c(2002, 2010))
        ),
        
        wellPanel (
            selectInput(inputId = 'strategie',
                        label = p(strong('Trading strategie')),
                        choices = list('Dual moving-average' = 'DualMA',
                                       'Momentum' = 'Momentum',
                                    'Buy and hold' = 'BuyAndHold'),
                        selected = 'Buy and hold'),

            checkboxInput(inputId = "debug", label="Debug"),

            conditionalPanel(condition = "input.strategie == 'DualMA'",
                            numericInput('longW', 'Long window', 100),
                            sliderInput(inputId = 'shortW', label = 'Short window', 
                                        min = 0.1, max = 1, step = 0.05, value = 0.75),
                            numericInput('threshold', 'Threshold', 0)),

            conditionalPanel(condition = "input.strategie == 'Momentum'",
                            numericInput('window', 'Moving average window', 3))
        ),
        
        wellPanel (
            selectInput(inputId = 'manager',
                        label = p(strong('Portfolio Manager')),
                        choices = list('Equity' = 'Equity',
                                    'Optimal Frontier' = 'OptimalFrontier'),
                        selected = 'Equity'),

            conditionalPanel(condition = "input.manager == 'OptimalFrontier'",
                            numericInput('loopback', 'Loopback period', 50),
                            textInput("source", "Data source", value="mysql")

        )),


        #submitButton("Backtest")
        checkboxInput(inputId = "done", label = "Update database")
  ),
  
  mainPanel(
    conditionalPanel(condition = "$('html').hasClass('shiny-busy')",
                     p(strong("Computing your trades..."))),

    conditionalPanel(condition = "!$('html').hasClass('shiny-busy') && input.done",
                     p(strong('Done !'))),

    tabsetPanel(
        tabPanel('Plot', h4('Trades backtest results'),
                 plotOutput(outputId = 'performance'),
                 br(), br(),
                 plotOutput('distribution'),
                 br(), br(),
                 plotOutput('relations'),
                 br(), br(),
                 plotOutput('rollperfs'),
                 br(), br(),
                 plotOutput('rollregression'),
                 br(), br(),
                 plotOutput('snailtrail'),
                 br(), br(),
                 plotOutput('plotcorr'),
                 br(), br(),
                 plotOutput('regression'),
                 br(), br(),
                 downloadButton('dlReport', 'Download Report')
        ),
        tabPanel('Statistics',
                 h4('Summary'),
                 tableOutput("stats"),
                 br(), br(),
                 h4('CAPM'),
                 tableOutput("capm"),
                 br(), br(),
                 h4('Annualized returns'),
                 tableOutput("annualizedRets"),
                 br(), br(),
                 h4('Benchmark correlation'),
                 tableOutput('correlation'),
                 br(), br(),
                 h4('Drawdown'),
                 br(), br(),
                 tableOutput('drawdown')
        ),
        tabPanel('Data', h4('Raw data from simulation'),
                 verbatimTextOutput('outhead'),
                 br(), br(),
                 verbatimTextOutput(outputId = 'results'),
                 br(), br(),
                 downloadButton('dlData', 'Download Data')
        ),
        tabPanel('About',
                p('This application computes given trading strategies and provides a portfolio analysis.'),
                'The underlaying backtest engine use the open source ', 
                a('Zipline', href='https://github.com/quantopian/zipline'), 
                'system, from ',
                a('Quantopian', href='https://www.quantopian.com'),
                '.', br(), 'The web application is built with the amazing', 
                a("Shiny.", href="http://www.rstudio.com/shiny"),
                br(), br(),
                strong('Author'), p('Xavier Bruhiere, mecatronics and power systems engineer.'), 
                br(),
                strong('Code'), p('Original source code available among other at', 
                                a('GitHub', href='https://github.com/Gusabi/QuanTrade'))
        ))
    )
))
