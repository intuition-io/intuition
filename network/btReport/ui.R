library(shiny)
 
# Define UI for dataset viewer application
shinyUI(pageWithSidebar(
  
    # Application title
    headerPanel("QuanTrade backtester front-end"),
  
    # Sidebar with controls to select a dataset and specify the number
    # of observations to view
    sidebarPanel(

        wellPanel(
            numericInput("amount", "Portfolio value:", 10000),

            textInput("ticker", "Action", value="starbucks"),    

            sliderInput(inputId = 'dateSlider', label = 'Period to trade',
                        min = 2000, max= 2012, value = c(2002, 2010))
        ),
        
        wellPanel (
            selectInput(inputId = 'strategie',
                        label = 'Trading strategie',
                        choices = c('Dual moving-average' = 'DualMA',
                                    'Buy and hold' = 'BuyAndHold'),
                        selected = 'Buy and hold'),

            conditionalPanel(
                        condition = 'input.strategie == DualMA',
                        numericInput('longW', 'Long window', 200),
                        sliderInput(inputId = 'shortW', label = 'Short window', 
                                    min = 0.1, max = 1, step = 0.05, value = 0.75)
                             )
        ),

        submitButton("Backtest")
  ),
  
  # Show a summary of the dataset and an HTML table with the requested
  # number of observations
  mainPanel(
    verbatimTextOutput(outputId = 'request'),
    plotOutput('performance'),
    tableOutput('correlation'),
    tableOutput("stats"),

    plotOutput('distribution'),

    plotOutput('relations'),

    tableOutput('drawdown')
  )
))
