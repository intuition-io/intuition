# http://www.quintuitive.com/2012/11/30/trading-with-support-vector-machines-svm/

#require(e1071)
require(quantmod)
require(parallel)
require(multicore)

source("e1071.R")

#tt = get( getSymbols( "^GSPC", from="1990-01-01" ) )
# Get usual OLHCV data
tt = get( getSymbols( "GOOG", from="2005-01-01" ) )

rets = na.trim( ROC( Cl( tt ), type="discrete" ) )

# only the first two features so that we may see some results in reasonable time
data = svmFeatures( tt )[,c(1,2)]

rets = rets[index(data)]
data = data[index(rets)]
stopifnot( NROW( rets ) == NROW( data ) )

forecast = svmComputeForecasts(
               data=data,
               history=500,
               response=rets,
               cores=2,
               trace=TRUE,
               modelPeriod="days",
               startDate="2013-04-09",
               endDate="2013-04-12",
               featureSelection="all" )

print('---------------------------------------------------')
print(forecast)

# An other attempt (list of 3):
    #http://quantumfinancier.wordpress.com/2010/05/21/application-of-svms/
    #http://quantumfinancier.wordpress.com/2010/06/10/svm-classification-using-rsi-from-various-lengths/
    #http://quantumfinancier.wordpress.com/2010/06/26/support-vector-machine-rsi-system/
