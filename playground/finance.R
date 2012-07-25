# Graphic management
trade_plot <- function(data, name, macd = 0, msg = "Google Quote and Volume plotting") 
{
	company <- paste(name,".pdf",sep="") 
	pdf(company)

    print(macd)

	## candleChart(x2, subset='2000-01-01 09::2000-01-01 10')
	## or reChart(major.ticks='days', subset='first 100 minutes')
	## chartSeries(trade_xts,multi.col=TRUE,theme="black")
	## candleChart(trade_xts, TA=NULL)
	## chartSeries(to.minutes10(x2),multi.col=TRUE,theme=chartTheme("black.mono"))
	blacktrade <- chartTheme(up.col='green',dn.col='red', area='#080808',bg.col='#000000')
    candleChart(data, theme=blacktrade, TA='addVo();addBBands();addDPO()')
    #addTA(volatility(OHLC(trade_xts),calc='garman.klass'), col=2)
    #addVolatility()
	## or chartSeries(trade_xts, theme="black", TA="addCCI();addMACD()")

    if ( macd > 0 ) {
        addMACD()
    }

	dev.off()
}


#MA exponential
ema = function(x, lambda = 0.97) {
	y = x[1]
	for (i in 2:length(x)) y[i] = lambda * y[i-1] + (1 - lambda) * x[i]
	return(y)
}

