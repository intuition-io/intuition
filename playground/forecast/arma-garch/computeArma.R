suppressPackageStartupMessages(library( quantmod ))
suppressPackageStartupMessages(library( fArma ))
 
source("armaForecast.R")

getSymbols("SPY", from="1950-01-01")
spyRets = diff(log(Ad(SPY)))
#spyArma = armaFit( ~arma(0, 2), data=as.ts( tail( spyRets, 500 ) ) )
#as.numeric( predict( spyArma, n.ahead=1, doplot=F )$pred )


# Window advice: 250-500
# Parameter distribution for the residuals, see link
# Daily model update
# Garch: usualy (1, 1), then depends on volatility, modeled or not
# Metrics: stay with AIC but not much difference with BIC, SIC, ...

# http://www.quintuitive.com/2012/12/27/armagarch-experiences/
# http://www.quintuitive.com/2012/08/22/arma-models-for-trading/
results = armaComputeForecasts(spyRets, maxOrder=c(4,4), save=TRUE, history=300, 
                               startDate="1990-01-01", cores=2, trace=TRUE)
print(results)

#TODO Save results$forecasts to gspcInd.csv

