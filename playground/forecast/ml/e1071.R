svmComputeOneForecast = function(
      id,
      data,
      response,
      startPoints,
      endPoints,
      len,
      history=500,
      trace=FALSE,
      kernel="radial",
      gamma=10^(-5:-1),
      cost=10^(0:2),
      sampling="cross",
      seed=1234,
      featureSelection=c("add", "prune", "all"),
      cross=10)
{
   # Determine the forecast length
   startIndex = startPoints[id]
   endIndex = endPoints[id]

   forecastLength = endIndex - startIndex + 1

   # A row in the data is responsible for the corresponding value in the
   # response. Thus, to forecast day X, we train the model on the previous
   # *history* days, and then use the features for day X to forecast.
   xtsData = data[index(data)[(startIndex-history):(startIndex-1)]]
   xtsResponse = response[index(response)[(startIndex-history):(startIndex-1)]]

   # Convert the input data and response to a matrix and a vector, respectively
   xx = as.matrix( coredata( xtsData ) )
   yy = as.vector( coredata( xtsResponse ) )

   # We need to set the seed to have reprodcible results
   set.seed( seed )

   if(featureSelection[1] == "add") {
      # We add the features one by one, until we cannot improve the error
      best = NULL
      bestPerf = 1e9

      # Maintained sorted, the content are the column indexes in the original matrix
      features = c()
      availableFeatures = seq(1,ncol(xx))

      # Use greedy approach to add features
      repeat {
         bestColIdToAdd = 0L
         # print( features )
         for(colId in 1:length(availableFeatures)) {
            # Get the matrix for the current tunning and tune
            zz = xx[,sort(c(features, availableFeatures[colId]))]
            # print(paste(sep="", "trying adding feature ", availableFeatures[colId]))
            newSvm = tune( svm,
                           train.x=zz,
                           train.y=yy,
                           ranges=list( gamma=gamma, cost=cost ),
                           tunecontrol=tune.control( sampling=sampling, cross=cross ),
                           kernel=kernel )
            # Check the performance improvement
            newPerf = round(newSvm$best.performance, 8)
            # print( paste( sep="", "new performance=", newPerf ) )
            if(newPerf < bestPerf) {
               # print( paste( sep="", "old performance=", bestPerf, ", new performance=", newPerf ) )
               best = newSvm
               bestPerf = newPerf
               bestColIdToAdd = colId
            }
         }

         if(bestColIdToAdd > 0) {
            # print( paste( sep="", "improvement, adding feature ", availableFeatures[bestColIdToAdd] ) )

            # Found an improvement, update the features
            features = sort(c(features, availableFeatures[bestColIdToAdd]))
            availableFeatures = availableFeatures[-bestColIdToAdd]

            # Exit if no features left
            if(length(availableFeatures) == 0) break
         } else {

            # No improvements, done
            break
         }
      }
   } else {
      # Train the SVM
      # ss = svm( x=xx, y=yy, kernel=kernel, gamma=gamma[1], cost=cost[1] )
      best = tune( svm,
                   train.x=xx,
                   train.y=yy,
                   ranges=list( gamma=gamma, cost=cost ),
                   tunecontrol=tune.control( sampling=sampling, cross=cross ),
                   kernel=kernel )

      # print( "gotBest" )
      # print( paste( sep="", "performance=", round( best$best.performance, 6 ) ) )

      # An array to keep track of the original participating features (by index)
      features = seq(1,ncol(xx))

      # print( length( features ) )

      # Use greedy approach to prune features
      if(featureSelection[1] == "prune") {
         repeat {
            bestColIdToRemove = 0L
            # print( features )
            for(colId in 1:ncol(xx)) {
               # Remove column colId
               zz = xx[,-colId]

               # print( paste( sep="", "trying without feature ", colId ) )

               # Tune with the reduced number of columns
               newBest = tune( svm,
                               train.x=zz,
                               train.y=yy,
                               ranges=list( gamma=gamma, cost=cost ),
                               tunecontrol=tune.control( sampling=sampling, cross=cross ),
                               kernel=kernel )
               # print( paste( sep="", "new performance=", round( newBest$best.performance, 6 ) ) )
               if(round( newBest$best.performance, 6 ) < round( best$best.performance, 6)) {
                  best = newBest
                  bestColIdToRemove = colId
                  # print( paste( sep="", "old performance=", round( best$best.performance, 6 ),
                  #              ", new performance=", round( newBest$best.performance, 6 ) ) )
               }
            }

            if(bestColIdToRemove > 0) {
               # Found an improvement
               xx = xx[,-bestColIdToRemove]
               features = features[-bestColIdToRemove]

               # print( paste( sep="", "improvement, removed feature ", bestColIdToRemove ) )

               # Break if there is only a single feature left
               if(length(features) == 1) break
            } else {
               # No improvements, done
               break
            }
         }
      }
   }

   # print( paste( sep="", "final features: (", paste( sep=",", collapse=",", features ), ")" ) )

   # Predict using the SVM, use only the remaining features
   xtsNewData = data[index(data)[startIndex:endIndex]]
   newData    = as.matrix( coredata( xtsNewData[,features] ) )
   fore       = predict( best$best.model, newData )

   if( trace ) {
      str = paste( sep="",
                       "\n", index(response)[startIndex], "\n",
                       "=======================\n",
                       "   from: ", head(index(xtsResponse),1),
                       ", to: ", tail(index(xtsResponse),1),
                       ", length: ", length(index(xtsResponse)),
                       "\n   new data: from: ", head(index(xtsNewData), 1),
                       ", to: ", tail(index(xtsNewData), 1),
                       ", length: ", NROW(xtsNewData),
                       "\n   forecast length: ", forecastLength,
                       "\n   best model performance: ", round( best$best.performance, 6 ),
                       "\n   best model features: (", paste( collapse=",", features), ")",
                       "\n   best model gamma: ", best$best.model$gamma,
                       "\n   best model cost: ", best$best.model$cost,
                       "\n   forecasts: ",
                       paste( collapse=", ", round( fore, 6 ) ),
                       "\n" )
      cat( sep="", str )
   }

   return( list( index=startIndex,
                 forecasts=fore,
                 performance=best$best.performance,
                 features=features,
                 gamma=best$best.model$gamma,
                 cost=best$best.model$cost ) )
}

svmComputeForecasts = function(
      data,
      response,
      history=500,
      modelPeriod="days",
      modelPeriodMultiple=1,
      trace=TRUE,
      startDate,
      endDate,
      kernel="radial",
      gamma=10^(-5:-1),
      cost=10^(0:2),
      sampling="cross",
      cross=10,
      featureSelection=c("add", "prune", "all"),
      cores)
{
   require( e1071 )

   stopifnot( NROW( data ) == NROW( response ) )

   len = NROW( response )

   # Determine the starting index
   if( !missing( startDate ) )
   {
      startIndex = max( len - NROW( index( data[paste( sep="", startDate, "/" )] ) ) + 1,
                        history + 2 )
   }
   else
   {
      startIndex = history + 2
   }

   # Determine the ending index
   if( missing( endDate ) )
   {
      lastIndex = len
   }
   else
   {
      lastIndex = NROW( index( data[paste( sep="", "/", endDate )] ) )
   }

   if( startIndex > lastIndex )
   {
      return( NULL )
   }

   modelPeriod = tolower( modelPeriod[1] )

   forecasts    = rep( NA, len )
   gammas       = rep( NA, len )
   costs        = rep( NA, len )
   performances = rep( NA, len )
   features     = rep( "", len )

   # Get the interesting indexes
   periods = index(data)[startIndex:lastIndex]

   # Compute the end points for each period (day, week, month, etc)
   endPoints = endpoints( periods, modelPeriod, modelPeriodMultiple )

   # Compute the starting points of each period, relative to the *data* index
   startPoints = endPoints + startIndex

   # Remove the last start point - it's outside
   length(startPoints) = length(startPoints) - 1

   # Make the end points relative to the *data* index
   endPoints = endPoints + startIndex - 1

   # Remove the first end point - it's always zero
   endPoints = tail( endPoints, -1 )

   stopifnot( length( endPoints ) == length( startPoints ) )

   if( missing( cores ) ) {
      cores = 1
   }

   res = mclapply( seq(1,length(startPoints)),
                   svmComputeOneForecast,
                   data=data,
                   response=response,
                   startPoints=startPoints,
                   endPoints=endPoints,
                   len=len,
                   history=history,
                   trace=TRUE,
                   kernel=kernel,
                   gamma=gamma,
                   cost=cost,
                   featureSelection=featureSelection,
                   mc.cores=cores )
   for( ll in res )
   {
      # Prepare the indexes 
      ii = ll[["index"]]
      jj = ii + NROW( ll[["forecasts"]] ) - 1

      # Copy the output
      forecasts[ii:jj] = ll[["forecasts"]]
      gammas[ii:jj] = ll[["gamma"]]
      costs[ii:jj] = ll[["cost"]]
      performances[ii:jj] = ll[["performance"]]

      # Encode the participating features as a bit mask stored in a single
      # integer. This representation limits us to max 32 features.
      features[ii:jj] = sum( 2^( ll[["features"]] - 1 ) )
   }

   sigUp = ifelse( forecasts >= 0, 1, 0 )
   sigUp[is.na( sigUp )] = 0

   sigDown = ifelse( forecasts < 0, -1, 0 )
   sigDown[is.na( sigDown)] = 0

   # forecasts[is.na( forecasts )] = 0

   sig = sigUp + sigDown

   res = merge( reclass( sig, response ),
                reclass( sigUp, response ),
                reclass( sigDown, response ),
                na.trim( reclass( forecasts, response ) ),
                reclass( performances, response ),
                reclass( gammas, response ),
                reclass( costs, response ),
                reclass( features, response ),
                all=F )
   colnames( res ) = c( "Indicator", "Up", "Down", "Forecasts", "Performance", "Gamma", "Cost", "Features" )

   return( res )
}


svmFeatures = function(series)
{
   require(PerformanceAnalytics)

   close = Cl(series)

   rets = na.trim(ROC(close, type="discrete"))

   # 1-day, 2-day, 3-day, 5-day, 10-day, 20-day and 50-day returns
   res = merge(na.trim(lag(rets, 1)),
               na.trim(lag(ROC(close, type="discrete", n=2), 1)),
               na.trim(lag(ROC(close, type="discrete", n=3), 1)),
               na.trim(lag(ROC(close, type="discrete", n=5), 1)),
               na.trim(lag(ROC(close, type="discrete", n=10), 1)),
               na.trim(lag(ROC(close, type="discrete", n=20), 1)),
               na.trim(lag(ROC(close, type="discrete", n=50), 1)),
               all=FALSE)

   # Add mean, median, sd, mad, skew and kurtosis
   res = merge(res,
               xts(na.trim(lag(rollmean(rets, k=21, align="right"),1))),
               xts(na.trim(lag(rollmedian(rets, k=21, align="right"),1))),
               xts(na.trim(lag(rollapply(rets, width=21, align="right", FUN=sd),1))),
               xts(na.trim(lag(rollapply(rets, width=21, align="right", FUN=mad),1))),
               xts(na.trim(lag(rollapply(rets, width=21, align="right", FUN=skewness),1))),
               xts(na.trim(lag(rollapply(rets, width=21, align="right", FUN=kurtosis),1))),
               all=FALSE)

   # Add volume with a lag of two
   res = merge(res, xts(na.trim(lag(Vo(series),2))), all=FALSE)

   colnames(res) = c("ROC.1", "ROC.2", "ROC.3", "ROC.5", "ROC.10", "ROC.20", "ROC.50",
                     "MEAN", "MEDIAN", "SD", "MAD", "SKEW", "KURTOSIS",
                     "VOLUME")

   return(res)
}


# Python rpy use help
require(quantmod)
getReturns = function(ohlcvData)
{
    return ( na.trim( ROC(Cl(ohlcvData), type="discrete") ) )
}

getSVMFeatures = function(ohlcvData)
{
    return ( svmFeatures(ohlcvData)[, c(1, 2)] )
}

predict = function(symbol, date=Sys.Date(), history=500)
{
    require(quantmod)
    tt = get( getSymbols(symbol, from=date - history ) )

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
                   cores=4,
                   trace=TRUE,
                   modelPeriod="days",
                   startDate="2012-03-09",
                   endDate="2012-03-12",
                   featureSelection="all" )
    print(forecast)
    return(forecast)
}
