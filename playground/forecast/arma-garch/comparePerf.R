library(quantmod)
library(lattice)
library(timeSeries)
 
getSymbols("^GSPC", from="1900-01-01")
 
gspcRets = Ad(GSPC) / lag(Ad(GSPC)) - 1
gspcRets[as.character(head(index(Ad(GSPC)),1))] = 0
 
# The maximum draw down
head(drawdownsStats(as.timeSeries(gspcRets)),10)
 
# The largest dropdawn is:
#         From     Trough         To      Depth Length ToTrough Recovery
# 1 2007-10-10 2009-03-09 2012-09-28 -0.5677539   1255      355       NA
 
# Load the ARMA indicator
gspcArmaInd = as.xts( read.zoo(file="gspcInd.csv", format="%Y-%m-%d", header=T, sep=",") )
 
# Filter out only the common indexes
mm = merge( gspcArmaInd[,1], gspcRets, all=F )
gspcArmaRets = mm[,1] * mm[,2]
 
# The maximum draw down
head(drawdownsStats(as.timeSeries(gspcArmaRets)),10)
# The largest dropdawn is:
#          From     Trough         To      Depth Length ToTrough Recovery
# 1  1987-10-26 1992-10-09 1997-10-27 -0.5592633   2531     1255     1276
 
gspcArmaGrowth = log( cumprod( 1 + gspcArmaRets ) )
 
gspcBHGrowth = log( cumprod( 1 + mm[,2] ) )
 
gspcAllGrowth = merge( gspcArmaGrowth, gspcBHGrowth, all=F )
 
xyplot( gspcAllGrowth,
        superpose=T,
        col=c("darkgreen", "darkblue"),
        lwd=2,
        key=list( x=.01,
                  y=0.95,
                  text=list(c("ARMA", "Buy-and-Hold")),
                  lines=list(lwd=2, col=c("darkgreen", "darkblue"))))
