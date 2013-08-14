#Packages required
require(PerformanceAnalytics)
require(quantmod)
require(car)

source('global.R')
 
#Here we get the symbols for the SP500 (GSPC), AAPL, and 5yr Treasuries (GS5)
getSymbols("^GSPC", src = "yahoo", from = as.Date("2008-01-01"), to = as.Date("2011-12-31"))
getSymbols("AAPL", src = "yahoo", from = as.Date("2009-01-01"), to = as.Date("2011-12-31"))
getSymbols("GS5", src = "FRED", from = as.Date("2008-12-01"), to = as.Date("2011-12-31"))
 
#Market risk R_m is the arithmetic mean of SP500 from 2009 through 2011
#Riskfree rate is arithmetic mean of 5yr treasuries
marketRisk<- mean(yearlyReturn(GSPC['2009::2011']))
riskFree <- mean(GS5['2009::2011'])
 
#My professor advised us to use weekly returns taken on wednesday
#so I take a subset of wednesdays and use the quantmod function
#weeklyReturn()
AAPL.weekly <- subset(AAPL,weekdays(time(AAPL))=='Wednesday')
AAPL.weekly <- weeklyReturn(AAPL['2009::2011'])
GSPC.weekly <- subset(GSPC,weekdays(time(GSPC))=='Wednesday')
GSPC.weekly <- weeklyReturn(GSPC['2009::2011'])
 
#Here I use PerformanceAnalytics functions for alpha+beta
#Then we calculate Cost of equity using our calculated figures
AAPL.beta <- CAPM.beta(AAPL.weekly,GSPC.weekly)
AAPL.alpha <- CAPM.alpha(AAPL.weekly,GSPC.weekly)
AAPL.expectedReturn <- riskFree + AAPL.beta * (marketRisk-riskFree)
 
#For my graph, I want to show R^2, so we get it from the
#lm object AAPL.reg
AAPL.reg<-lm(AAPL.weekly~GSPC.weekly)
AAPL.rsquared<-summary(AAPL.reg)$r.squared
 
#Lastly, we graph the returns and fit line, along with info
scatterplot(100*as.vector(GSPC.weekly),100*as.vector(AAPL.weekly), smooth=FALSE, main='Apple Inc. vs. S&P 500 2009-2011',xlab='S&P500 Returns', ylab='Apple Returns',boxplots=FALSE)
text(5,-10,paste('y = ',signif(AAPL.alpha,digits=4),' + ',signif(AAPL.beta,digits=5),'x \n R^2 = ',signif(AAPL.rsquared,digits=6),'\nn=',length(as.vector(AAPL.weekly)),sep=''),font=2)
