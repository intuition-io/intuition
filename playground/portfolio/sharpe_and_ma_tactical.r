require(lattice)
require(latticeExtra)
require(reshape2)
require(directlabels)
require(quantmod)
require(PerformanceAnalytics)

getSymbols("^GSPC",from="1900-01-01")

GSPC.monthly <- GSPC[endpoints(GSPC,"months"),4]
GSPC.roc <- ROC(GSPC.monthly,type="discrete",n=1)

#apply.rolling with SharpeRatio as FUN gives error
#so I started playing with variations of Sharpe
sharpe <- (apply.rolling(GSPC.roc+1,FUN=prod,width=12)-1)/(runMax(abs(GSPC.roc),n=3))

systems <- merge(GSPC.roc,
                 lag(ifelse(GSPC.monthly > runMean(GSPC.monthly,n=10),1,0))*GSPC.roc,
                 lag(ifelse(sharpe > runMean(sharpe,n=10),1,0))*GSPC.roc,
                 lag(ifelse(sharpe > 0,1,0))*GSPC.roc,
                 lag(ifelse(sharpe > lag(sharpe,k=6),1,0))*GSPC.roc)
colnames(systems) <- c("SP500","MovAvgPrice","MovAvgSharpe","Sharpe>0","Sharpe>6moPrior")

#publicize the fine work at http://tradeblotter.wordpress.com/2012/06/04/download-and-parse-edhec-hedge-fund-indexes/
#all code for next two charts comes from the post
#I deserve no credit

# Cumulative returns and drawdowns
par(cex.lab=.8) # should set these parameters once at the top
op <- par(no.readonly = TRUE)
layout(matrix(c(1, 2)), height = c(2, 1.3), width = 1)
par(mar = c(1, 4, 4, 2))
chart.CumReturns(systems, main = "S&P 500 with Tactical Overlays",
                 xaxis = FALSE, legend.loc = "topleft", ylab = "Cumulative Return",
                 #use colors from latticeExtra theEconomist theme so colors will be consistent
                 colorset= theEconomist.theme()$superpose.line$col, ylog=TRUE,
                 wealth.index=TRUE, cex.legend=.7, cex.axis=.6, cex.lab=.7)
abline(v=which(index(systems)=="1985-12-31"),col="red",lty=2)
text(x=which(index(systems)=="1985-12-31")+2,y=1,labels="Dividing Line in Result",adj=0,srt=90,cex=0.7,col="red")
par(mar = c(5, 4, 0, 2))
chart.Drawdown(systems, main = "", ylab = "Drawdown", colorset = theEconomist.theme()$superpose.line$col, cex.axis=.6, cex.lab=.7)
abline(v=which(index(systems)=="1985-12-31"),col="red",lty=2)
par(op)




# Generate charts of with ETL and VaR through time
#caution: this takes about 10 minutes to complete
par(mar=c(3, 4, 0, 2) + 0.1) #c(bottom, left, top, right)
charts.BarVaR(systems, p=(1-1/12), gap=36, main="", show.greenredbars=TRUE, 
              methods=c("ModifiedES", "ModifiedVaR"), show.endvalue=TRUE, 
              colorset=rep("Black",7), ylim=c(-.1,.15))
par(op)


#do a lattice density plot so we can look at the distributions
#of monthly changes for each approach
systems.df <- as.data.frame(cbind(index(systems),coredata(systems)))
systems.melt <- melt(systems.df,id.vars=1)
colnames(systems.melt) <- c("date","system","monthROC")
dp <- densityplot(~monthROC,groups=system,data=systems.melt,
            par.settings = theEconomist.theme(box = "transparent"),
            lattice.options = theEconomist.opts(),
            ylim=c(0,125),
            xlab=NULL,
            main="Density Plot of Monthly Change in S&P 500 with Tactical Overlays")
direct.label(dp,top.bumptwice)

#density plot reveals very different distributions
#so get the skew and kurtosis for each approach
skew.kurtosis <- rbind(skewness(systems),kurtosis(systems))
skew.kurtosis.melt <- melt(cbind(rownames(skew.kurtosis),skew.kurtosis))
colnames(skew.kurtosis.melt) <- c("variable","system","value")

barchart(value~variable,group=system,data=skew.kurtosis.melt,
         origin=0,
         par.settings = theEconomist.theme(box = "transparent"),
         lattice.options = theEconomist.opts(),
         auto.key=list(space="right"),
         ylab=NULL,
         main="Skewness and Kurtosis of S&P 500 with Tactical Overlays")
