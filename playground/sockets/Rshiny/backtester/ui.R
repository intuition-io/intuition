library(shiny)
 
# Define UI for dataset viewer application
shinyUI(pageWithSidebar(
  
  # Application title
  headerPanel("Shiny Moving Average Parameter Test"),
  
  # Sidebar with controls to select a dataset and specify the number
  # of observations to view
  sidebarPanel(
    numericInput("nmonths", "Number of months for moving average:", 10),
    textInput("command", "Shell", value = ""),    
    submitButton("Backtest")
  ),
  
  # Show a summary of the dataset and an HTML table with the requested
  # number of observations
  mainPanel(
    h3(textOutput("command")),
    plotOutput("systemPlot"),
 
    tableOutput("view")
  )
))
