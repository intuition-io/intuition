# http://tradeblotter.wordpress.com/2013/01/18/visually-comparing-return-distributions/
# Histogram, QQPlot and ECDF plots aligned by scale for comparison
page.Distributions <- function (R, ...) {
    require(PerformanceAnalytics)
    op <- par(no.readonly = TRUE)
    # c(bottom, left, top, right)
    par(oma = c(5,0,2,1), mar=c(0,0,0,3))
    layout(matrix(1:(4*NCOL(R)), ncol=4, byrow=TRUE), widths=rep(c(.6,1,1,1),NCOL(R)))
    # layout.show(n=21)
    chart.mins=min(R, na.rm=TRUE)
    chart.maxs=max(R, na.rm=TRUE)
    row.names = sapply(colnames(R), function(x) paste(strwrap(x,10), collapse = "\n"), USE.NAMES=FALSE)
    for(i in 1:NCOL(R)){
        if(i==NCOL(R)){
            plot.new()
            text(x=1, y=0.5, adj=c(1,0.5), labels=row.names[i], cex=1.1)
            chart.Histogram(R[,i], main="", xlim=c(chart.mins, chart.maxs), 
                            breaks=seq(round(chart.mins, digits=2)-0.01, round(chart.maxs, digits=2)+0.01, by=0.01), 
                            show.outliers=TRUE, methods=c("add.normal"), colorset = 
                            c("black", "#00008F", "#005AFF", "#23FFDC", "#ECFF13", "#FF4A00", "#800000"))
            abline(v=0, col="darkgray", lty=2)
            chart.QQPlot(R[,i], main="", pch=20, envelope=0.95, col=c(1,"#005AFF"))
            abline(v=0, col="darkgray", lty=2)
            chart.ECDF(R[,i], main="", xlim=c(chart.mins, chart.maxs), lwd=2)
            abline(v=0, col="darkgray", lty=2)
        }
        else{
            plot.new()
            text(x=1, y=0.5, adj=c(1,0.5), labels=row.names[i], cex=1.1)
            chart.Histogram(R[,i], main="", xlim=c(chart.mins, chart.maxs), 
                            breaks=seq(round(chart.mins, digits=2)-0.01, round(chart.maxs, digits=2)+0.01, by=0.01), 
                            xaxis=FALSE, yaxis=FALSE, show.outliers=TRUE, methods=c("add.normal"), colorset = 
                            c("black", "#00008F", "#005AFF", "#23FFDC", "#ECFF13", "#FF4A00", "#800000"))
            abline(v=0, col="darkgray", lty=2)
            chart.QQPlot(R[,i], main="", pch=20, envelope=0.95, col=c(1,"#005AFF"))
            abline(v=0, col="darkgray", lty=2)
            chart.ECDF(R[,i], main="", xlim=c(chart.mins, chart.maxs), xaxis=FALSE, yaxis=FALSE, lwd=2)
            abline(v=0, col="darkgray", lty=2)
        }
    }
    par(op)
}

usage <- function()
{
    require(PerformanceAnalytics)
    data(edhec)
    page.Distributions(edhec[,c("Convertible Arbitrage", "Equity Market Neutral", "Fixed Income Arbitrage", 
                                "Event Driven", "CTA Global", "Global Macro", "Long/Short Equity")])
}
