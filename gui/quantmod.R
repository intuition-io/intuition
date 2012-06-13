#!/usr/bin/env Rscript

#This file scripts a R training for instance
print("-------------  R trade script  -------------")

#Initialisation
args <- commandArgs()
print("Loading quantmod library")
library(quantmod)
print("Entering in the right working directory")
setwd(getwd())
setwd("./data")

# Read the dowlonded quote file and store it in an object
print("Downloading data file in current directory")
FILE <- paste(args[4],".data",sep="") 
trade <- read.table(file = FILE, sep=",", na.strings="-", header=TRUE)
closes = trade[, "Close"]
opens = trade[, "Open"]
highs = trade[, "High"]
lows = trade[, "Low"]

print("DEBUG: before trade_xts assigment")
trade_xts <- xts(trade[,-1],seq(as.POSIXct("2000-01-01 9:00"),len=length(trade[,1]),by="min"))

## Some interested stuff
## periodicity(trade_xts)
## to.minutes5(trade_xts)
## trade_xts['2000-01-01 14::']
## trade_xts['2000-01-01 14','2000-01-01 15']
## last(x2,10)
## max(x2$Close)

# Print some control informations
print("Quick informations about the dowloaded file")
periodicity(trade_xts)
last(trade_xts$Close)
max(trade_xts$Close)
str(trade_xts)

print("More detailed informations about data in mentionned file")
summary(trade_xts$Open)
summary(trade_xts$Volume)
 
# Graphic management
trade_plot <- function(msg = "Google Quote and Volume plotting") 
{
 	print(msg)
	company <- paste(args[4],".bmp",sep="") 
	bmp(company)

	## candleChart(x2, subset='2000-01-01 09::2000-01-01 10')
	## or reChart(major.ticks='days', subset='first 100 minutes')
	## chartSeries(trade_xts,multi.col=TRUE,theme="black")
	## candleChart(trade_xts, TA=NULL)
	## chartSeries(to.minutes10(x2),multi.col=TRUE,theme=chartTheme("black.mono"))
	## blacktrade <- chartTheme(up.col='white',dn.col='red', area='#080808',bg.col='#000000')
	##candleChart(trade_xts,theme=blacktrade)
	candleChart(trade_xts,theme=chartTheme("black.mono"),TA="addMACD();addDEMA();addSMI();addCCI()")
	#addMACD()
	#addDEMA()
	#addSMI()
	#addBBands()
	#addDPO()
	#addCCI()
	## or chartSeries(trade_xts, theme="black", TA="addCCI();addMACD()")

	dev.off()
}


#MA exponential
ema = function(x, lambda = 0.97) {
	y = x[1]
	for (i in 2:length(x)) y[i] = lambda * y[i-1] + (1 - lambda) * x[i]
	return(y)
}

ma1 = ema(closes)
ma2 = ema(closes, 0.94)
conv = ma2 - ma1
save = c(conv[length(conv)], ma1[length(ma1)], ma2[length(ma2)])
#write.table(save, file=paste(args[4],".ana", sep=""), sep=" ")
capture.output(print(save), file=paste(args[4],".ana", sep=""))
#save(ma1[,:],ma2[,:],conv, file="truc.RData")

trade_plot("Calling trade_plot function")

# print("You can plot Quotes by using trade_plot function")

print("-------------------------------------")
