# http://www.r-bloggers.com/automatic-armagarch-selection-in-parallel/

garchAutoTryFit = function(
   ll,
   data,
   trace=FALSE,
   forecast.length=1,
   with.forecast=TRUE,
   ic="AIC",
   garch.model="garch" )
{
   formula = as.formula( paste( sep="",
                                "~ arma(", ll$order[1], ",", ll$order[2], ")+",
                                garch.model,
                                "(", ll$order[3], ",", ll$order[4], ")" ) )
   fit = tryCatch( garchFit( formula=formula,
                             data=data,
                             trace=FALSE,
                             cond.dist=ll$dist ),
                   error=function( err ) TRUE,
                   warning=function( warn ) FALSE )
 
   pp = NULL
 
   if( !is.logical( fit ) ) {
      if( with.forecast ) {
         pp = tryCatch( predict( fit,
                                 n.ahead=forecast.length,
                                 doplot=FALSE ),
                        error=function( err ) FALSE,
                        warning=function( warn ) FALSE )
         if( is.logical( pp ) ) {
            fit = NULL
         }
      }
   } else {
      fit = NULL
   }
 
   if( trace ) {
      if( is.null( fit ) ) {
         cat( paste( sep="",
                     "   Analyzing (", ll$order[1], ",", ll$order[2],
                                    ",", ll$order[3], ",", ll$order[4], ") with ",
                                    ll$dist, " distribution done.",
                     "Bad model.\n" ) )
      } else {
         if( with.forecast ) {
            cat( paste( sep="",
                        "   Analyzing (", ll$order[1], ",", ll$order[2], ",",
                                          ll$order[3], ",", ll$order[4], ") with ",
                                          ll$dist, " distribution done.",
                        "Good model. ", ic, " = ", round(fit@fit$ics[[ic]],6),
                        ", forecast: ",
                        paste( collapse=",", round(pp[,1],4) ), "\n" ) )
         } else {
            cat( paste( sep="",
                        "   Analyzing (", ll[1], ",", ll[2], ",", ll[3], ",", ll[4], ") with ",
                                          ll$dist, " distribution done.",
                        "Good model. ", ic, " = ", round(fit@fit$ics[[ic]],6), "\n" ) )
         }
      }
   }
 
   return( fit )
}
 
garchAuto = function(
       xx,
       min.order=c(0,0,1,1),
       max.order=c(5,5,1,1),
       trace=FALSE,
       cond.dists="sged",
       with.forecast=TRUE,
       forecast.length=1,
       arma.sum=c(0,1e9),
       cores=1,
       ic="AIC",
       garch.model="garch" )
{
   require( fGarch )
   require( parallel )
 
   len = NROW( xx )
 
   models = list( )
 
   for( dist in cond.dists )
   for( p in min.order[1]:max.order[1] )
   for( q in min.order[2]:max.order[2] )
   for( r in min.order[3]:max.order[3] )
   for( s in min.order[4]:max.order[4] )
   {
      pq.sum = p + q
      if( pq.sum <= arma.sum[2] && pq.sum >= arma.sum[1] )
      {
         models[[length( models ) + 1]] = list( order=c( p, q, r, s ), dist=dist )
      }
   }
 
   res = mclapply( models,
                   garchAutoTryFit,
                   data=xx,
                   trace=trace,
                   ic=ic,
                   garch.model=garch.model,
                   forecast.length=forecast.length,
                   with.forecast=TRUE,
                   mc.cores=cores )
 
   best.fit = NULL
 
   best.ic = 1e9
   for( rr in res )
   {
      if( !is.null( rr ) )
      {
         current.ic = rr@fit$ics[[ic]]
         if( current.ic < best.ic )
         {
            best.ic = current.ic
            best.fit = rr
         }
      }
   }
 
   if( best.ic < 1e9 )
   {
      return( best.fit )
   }
 
   return( NULL )
}


usageSample = function()
{
    library(quantmod)
     
    spy = getSymbols("SPY", auto.assign=FALSE)
    rets = ROC(Cl(spy), na.pad=FALSE)
    fit = garchAuto(rets, cores=8, trace=TRUE)
}
