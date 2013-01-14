armaTryFit = function(
                      ll,  
                      data,
                      trace=FALSE,
                      includeMean=TRUE, 
                      withForecast=TRUE,
                      forecastLength=1 )
{
    formula = as.formula( paste( sep="",
                                "xx ~ arma(", ll[1], ",", ll[2], ")" ) )

    fit = tryCatch( armaFit( formula=formula,
                            data=data,
                            include.mean=includeMean ),
                   error=function( err ) FALSE,
                   warning=function( warn ) FALSE )

    pp = NULL 

    if( !is.logical( fit ) )
    {
        if( withForecast )
        {    
            pp = tryCatch( predict( fit, n.ahead=forecastLength, doplot=F ),
                          error=function( err ) FALSE,
                          warning=function( warn ) FALSE )
            if( is.logical( pp ) )
            {    
                fit = NULL 
            }    
        }    
    }
    else 
    {
        fit = NULL 
    }

    if( trace )
    {
        if( is.null( fit ) )
        {    
            cat( paste( sep="",
                       "   Analyzing (", ll[1], ",", ll[2], ") done.",
                       "Bad model.\n" ) )
        }    
        else 
        {    
            if( withForecast )
            {    
                cat( paste( sep="",
                           "   Analyzing (", ll[1], ",", ll[2], ") done.",
                           "Good model. AIC = ", round(fit@fit$aic,6),
                           ", forecast: ", round(pp$pred[1],6), "\n" ) )
            }    
            else 
            {    
                cat( paste( sep="",
                           "   Analyzing (", ll[1], ",", ll[2], ") done.",
                           "Good model. AIC = ", round(fit@fit$aic,6), ".\n" ) )
            }    
        }    
    }

    return( fit )
}

# Improvement: arma(p+1, p)
armaSearch = function(
                      xx,
                      minOrder=c(0,0),
                      maxOrder=c(5,5),
                      trace=FALSE,
                      includeMean=TRUE,
                      withForecast=TRUE,
                      forecastLength=1,
                      paramSum=c(1,1e9),
                      cores )
{
    require( fArma )
    require( parallel )

    len = NROW( xx )

    if( missing( cores ) )
    {
        cores = 1
    }

    models = list( )

    for( p in minOrder[1]:maxOrder[1] )
        #for( q in minOrder[2]:maxOrder[2] )
        #{
        q = p+1
        pqSum = p + q
        if( pqSum <= paramSum[2] && pqSum >= paramSum[1] )
        {
            models[[length( models ) + 1]] = c( p, q )
        }
        #}

    res = mclapply( models,
                   armaTryFit,
                   data=as.ts(xx),
                   trace=trace,
                   includeMean=includeMean,
                   withForecast=TRUE,
                   forecastLength=forecastLength,
                   mc.cores=cores )

    bestIc = 1e9
    bestFit = NULL

    for( rr in res )
    {
        if( !is.null( rr ) )
        {
            ic = rr@fit$aic
            if( ic < bestIc )
            {
                bestIc = ic
                bestFit = rr
            }
        }
    }

    if( bestIc < 1e9 )
    {
        return( bestFit )
    }

    return( NULL )
}

armaComputeForecasts = function(
                                x,
                                history=500,
                                minOrder=c(0,0),
                                maxOrder=c(5,5),
                                trace=FALSE,
                                save=FALSE,
                                paramSum=c(0,1e9),
                                includeMean=TRUE,
                                startDate,
                                endDate,
                                lags=1,
                                cores )
{
    stopifnot( is.xts( x ) )
    xx = x
    len = NROW( xx )

    if( !missing( startDate ) )
    { 
        startIndex = max( len - NROW( index( xx[paste( sep="", startDate, "/" )] ) ) + 1,
                         history + lags )
    }
    else
    { 
        startIndex = history + lags
    }

    if( missing( endDate ) )
    { 
        lastIndex = len
    }
    else
    { 
        lastIndex = NROW( index( xx[paste( sep="", "/", endDate )] ) )
    }

    if( startIndex > lastIndex )
    { 
        return( NULL )
    }

    currentIndex = startIndex
    nextIndex = 1

    forecasts = rep( NA, len )
    ars = rep( NA, len )
    mas = rep( NA, len )

    if( missing( cores ) )
    {
        cores = 1
    }

    repeat
    {
        nextIndex = currentIndex + 1
        forecastLength = nextIndex - currentIndex + lags - 1

        # Get the series
        yy = xx[index(xx)[(currentIndex-history-lags+1):(currentIndex-lags)]]

        if( trace )
        {
            cat( paste( sep="", "\n", index(xx)[currentIndex], "\n" ) )
            cat( paste( sep="", "=======================\n" ) )
            cat( paste( sep="",
                       "   from: ", head(index(yy),1 ),
                       ", to: ", tail(index(yy),1 ),
                       ", length: ", length( index( yy ) ),
                       "\n" ) )
            cat( paste( sep="",
                       "   forecast length: ", forecastLength, "\n\n" ) )
        }

        # Find the best fit
        bestFit = armaSearch(
                             yy,
                             minOrder=minOrder,
                             maxOrder=maxOrder,
                             paramSum=paramSum,
                             includeMean=includeMean,
                             withForecast=TRUE,
                             forecastLength=forecastLength,
                             trace=trace,
                             cores=cores )

        if( !is.null( bestFit ) )
        {
            order = bestFit@fit$arma

            if( trace )
            {
                cat( paste( sep="",
                           "   best model: (",
                           order[1], ",",
                           order[2], ")\n" ) )
            }

            # Forecast
            fore = tryCatch( predict( bestFit, n.ahead=forecastLength, doplot=FALSE ),
                            error=function( err ) FALSE,
                            warning=function( warn ) FALSE )
            if( !is.logical( fore ) )
            {
                # Save the forecast
                forecasts[currentIndex] = tail( fore$pred, 1 )

                # Save the model order
                ars[currentIndex] = order[1]
                mas[currentIndex] = order[2]

                if( trace )
                {
                    cat( sep="",
                        "\n   all long forecasts: ",
                        paste( collapse=", ",
                              round( fore$pred, 6 ) ),
                        "\n   forecasts: ",
                        paste( collapse=", ",
                              round( forecasts[currentIndex], 6 ) ),
                        "\n" )
                }
            }
            else
            {
                forecasts[currentIndex] = 0
            }
        }
        if ( save )
        {
            write.table(c(currentIndex, forecasts[currentIntex]), file="gspcInd.csv", sep=",")
        }

        if( nextIndex > len ) break
        currentIndex = nextIndex
    }

    sigUp = ifelse( forecasts > 0, 1, 0 )
    sigUp[is.na( sigUp )] = 0

    sigDown = ifelse( forecasts < 0, -1, 0 )
    sigDown[is.na( sigDown)] = 0

    forecasts[is.na( forecasts )] = 0

    sig = sigUp + sigDown

    res = merge( reclass( sig, x ), sigUp, sigDown, forecasts, ars, mas )
    colnames( res ) = c( "Indicator", "Up", "Down", "Forecasts", "ar", "ma" )

    return( res )
}
