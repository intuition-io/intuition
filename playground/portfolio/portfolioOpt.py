""" Construct a portfolio of equities that have high sharpe ratios
and low correlation to each other.  Script proceeds by:
    1. Reading data from every .csv file in the execution directory
    2. Calculating the sharpe ratios for each equity and sorting
    3. Taking the top _n_ equities according to sharpe ratio
    4. Computing a correlation matrix for those n equities
    5. Selecting a portfolio that minimizes the sum of cross-correlations
"""
import numpy as np
from numpy import recfromcsv
from itertools import combinations
import os

# Portfolio size is the number of instruments included in our 'best portfolio'
portfolio_size=4

# Stocks are sorted by sharpe ratio, then the top n stocks are analysed for cross-correlation
top_n_equities=10

# Get an array of file names in the current directory ending with csv
files = [fi for fi in os.listdir('.') if fi.endswith(".csv")]

# Grab a second array with just the names, for convenience.  These are used
# to name columns of data.
symbols = [os.path.splitext(fi)[0] for fi in files]

# Load one file so we can find out how many days of data are in it.
firstfile = recfromcsv(files[0])
datalength = len(firstfile['close'])

# Creates a 'record array', which is like a spreadsheet with a header.  The header is the
# symbol (filename without the csv extension), and the data is all floats.
closes = np.recarray((datalength,), dtype=[(symbol, 'float') for symbol in symbols])

# Do the same for daily returns, except one row smaller than closes.
daily_ret = np.recarray((datalength-1,), dtype=[(symbol, 'float') for symbol in symbols])

# Initialize some arrays for storing data
average_returns = np.zeros(len(files))
return_stdev = np.zeros(len(files))
sharpe_ratios = np.zeros(len(files))
cumulative_returns = np.recarray((datalength,), dtype=[(symbol, 'float') for symbol in symbols])

#  This loops over every filename.  'i' is the index into the array, which we use to
# add data to the other data structures we initialized.  That way the data for 'aapl' is
# at the same index in every data structure.
for i, file in enumerate(files):
    # Reads in the data from the file
    data = recfromcsv(file)              
    # Skip it if there isn't enough data - simplifies everything else
    if(len(data) != datalength):
        continue                             
    # Read the 'close' column of the data and reverse the numbers
    closes[symbols[i]] = data['close'][::-1]  

    # Get the closing price for the symbol - remember the columns are named by the symbol,
    # thus symbols[i] is the index into closes.  Tacking on the [1:] means from index 1 to the end,
    # adding [:-1] means from the second-last to the first, so we're subtracting day 1 from day 2, etc.
    daily_ret[symbols[i]] = (closes[symbols[i]][1:]-closes[symbols[i]][:-1])/closes[symbols[i]][:-1]

    # Now that we have the daily returns in %, calculate the relevant stats.  
    average_returns[i] = np.mean(daily_ret[symbols[i]])
    return_stdev[i] = np.std(daily_ret[symbols[i]])
    sharpe_ratios[i] = (average_returns[i] / return_stdev[i]) * np.sqrt(datalength)

# Now we have all ratios for all equities.  The next line doesn't sort them by sharpe, but it
# gives us the indexes of the sharpe_ratios array in order.  That is, an array [5, 3, 9, 2, 0] would
# return [4, 3, 1, 0, 2].
sorted_sharpe_indices = np.argsort(sharpe_ratios)[::-1][0:top_n_equities]

# Next we create a datastructure to hold the daily returns of the top n equities
cov_data = np.zeros((datalength-1, top_n_equities))

# The sorted_sharpe_indices has the indices, in order, of the top n sharpe ratios.  Grab
# the daily returns for those stocks and put them in our cov_data index (cov stands for
# covariate)
for i, symbol_index in enumerate(sorted_sharpe_indices):
    cov_data[:,i] = daily_ret[symbols[symbol_index]]

# Now make a correlation matrix for the top n equities
cormat = np.corrcoef(cov_data.transpose())

# Create all possible combinations of the n top equites for the given portfolio size.  
portfolios = list(combinations(range(0, top_n_equities), portfolio_size))

# For each possible combination of the top n equities, add up all the correlations
# between the four instruments
total_corr = [sum([cormat[x[0]][x[1]] for x in combinations(p, 2)]) for p in portfolios]

# Find the portfolio with the smallest sum of correlations, and convert that back into 
# the instrument names via a lookup in the symbols array
best_portfolio=[symbols[sorted_sharpe_indices[i]] for i in portfolios[total_corr.index(np.nanmin(total_corr))]]
print(best_portfolio)
