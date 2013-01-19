library("PerformanceAnalytics") #Load the PerformanceAnalytics library
 
#Load in our strategy performance spreadsheet
#Structure is: Date,Strategy1,Strategy2,Index
#Each row contains the period returns (% terms)
 
strategies <- read.zoo("strategyperfomance.csv", sep = ",", header = TRUE, format="%Y-%m-%d")
head(strategies)
 
#List all the column names to check data loaded in correctly
#Can access colums with strategies["columnname"]
colnames(strategies)
 
#Lets see how all the strategies faired against the index
charts.PerformanceSummary(strategies,main="Performance of all Strategies")
 
#Lets see how just strategy one faired against the index
charts.PerformanceSummary(strategies[,c("Strategy1","Index")],main="Performance of Strategy 1")
 
#Lets calculate a table of montly returns by year and strategy
table.CalendarReturns(strategies)
 
#Lets make a boxplot of the returns
chart.Boxplot(strategies)
 
#Set the plotting area to a 2 by 2 grid
layout(rbind(c(1,2),c(3,4)))
 
#Plot various histograms with different overlays added
chart.Histogram(strategies[,"Strategy1"], main = "Plain", methods = NULL)
chart.Histogram(strategies[,"Strategy1"], main = "Density", breaks=40, methods = c("add.density", "add.normal"))
chart.Histogram(strategies[,"Strategy1"], main = "Skew and Kurt", methods = c("add.centered", "add.rug"))
chart.Histogram(strategies[,"Strategy1"], main = "Risk Measures", methods = c("add.risk"))
 
#Note: The above histogram plots is taken from the example documentation
#The documentation is excellent
#http://cran.r-project.org/web/packages/PerformanceAnalytics/vignettes/PA-charts.pdf
