#MA exponential
ema <- function(x, lambda = 0.97) {
	y = x[1]
	for (i in 2:length(x)) y[i] = lambda * y[i-1] + (1 - lambda) * x[i]
	return(y)
}

