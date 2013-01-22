require(xts)
require(PerformanceAnalytics)

# Download the following file to the working directory:
# http://www.edhec-risk.com/indexes/pure_style/data/table/history.csv
readEDHEC <- function()
{
    x=read.csv(file="history.csv", sep=";", header=TRUE, check.names=FALSE)
    x.dates = as.Date(x[,1], format="%d/%m/%Y")
    x.data = apply(x[,-1], MARGIN=2, FUN=function(x){as.numeric(sub("%","", x, fixed=TRUE))/100}) # get rid of percentage signs
    edhec = xts(x.data, order.by=x.dates)
}

Performances <- function(series)
{
    # Cumulative returns and drawdowns
    par(cex.lab=.8) # should set these parameters once at the top
    op <- par(no.readonly = TRUE)
    layout(matrix(c(1, 2)), height = c(2, 1.3), width = 1)
    par(mar = c(1, 4, 4, 2))
    chart.CumReturns(series, main = "EDHEC Index Returns", xaxis = FALSE, legend.loc = "topleft", ylab = "Cumulative Return", colorset= rainbow8equal, ylog=TRUE, wealth.index=TRUE, cex.legend=.7, cex.axis=.6, cex.lab=.7)
    par(mar = c(5, 4, 0, 2))
    chart.Drawdown(series, main = "", ylab = "Drawdown", colorset = rainbow8equal, cex.axis=.6, cex.lab=.7)
    par(op)

    # Generate charts of EDHEC index returns with ETL and VaR through time
    par(mar=c(3, 4, 0, 2) + 0.1) #c(bottom, left, top, right)
    charts.BarVaR(series, p=(1-1/12), gap=36, main="", show.greenredbars=TRUE, 
                  methods=c("ModifiedES", "ModifiedVaR"), show.endvalue=TRUE, 
                  colorset=rep("Black",7), ylim=c(-.1,.15))
    par(op)
}

Distributions <- function(series) 
{
    par(oma = c(5,0,2,1), mar=c(0,0,0,3))
    layout(matrix(1:28, ncol=4, byrow=TRUE), widths=rep(c(.6,1,1,1),7))
    chart.mins=min(series)
    chart.maxs=max(series)
    row.names = sapply(colnames(series), function(x) paste(strwrap(x,10), collapse = "\n"), USE.NAMES=FALSE)
    for(i in 1:7){
        if(i==7){
            plot.new()
            text(x=1, y=0.5, adj=c(1,0.5), labels=row.names[i], cex=1.1)
            chart.Histogram(series[,i], main="", xlim=c(chart.mins, chart.maxs), breaks=seq(-0.15,0.10, by=0.01), show.outliers=TRUE, methods=c("add.normal"))
            abline(v=0, col="darkgray", lty=2)
            chart.QQPlot(series[,i], main="", pch="*", envelope=0.95, col=c(1,"#005AFF"))
            abline(v=0, col="darkgray", lty=2)
            chart.ECDF(series[,i], main="", xlim=c(chart.mins, chart.maxs), lwd=2)
            abline(v=0, col="darkgray", lty=2)
        }
        else{
            plot.new()
            text(x=1, y=0.5, adj=c(1,0.5), labels=row.names[i], cex=1.1)
            chart.Histogram(series[,i], main="", xlim=c(chart.mins, chart.maxs), breaks=seq(-0.15,0.10, by=0.01), xaxis=FALSE, yaxis=FALSE, show.outliers=TRUE, methods=c("add.normal"))
            abline(v=0, col="darkgray", lty=2)
            chart.QQPlot(series[,i], main="", pch="*", envelope=0.95, col=c(1,"#005AFF"))
            abline(v=0, col="darkgray", lty=2)
            chart.ECDF(series[,i], main="", xlim=c(chart.mins, chart.maxs), xaxis=FALSE, yaxis=FALSE, lwd=2)
            abline(v=0, col="darkgray", lty=2)
        }
    }
}

edhec <- readEDHEC()
# Drop some indexes and reorder
edhec.R = edhec[,c("Convertible Arbitrage", "Equity Market Neutral","Fixed Income Arbitrage", "Event Driven", "CTA Global", "Global Macro", "Long/Short Equity")]

#Performances(edhec.R)
#Distributions(edhec.R)
