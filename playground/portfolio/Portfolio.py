import numpy as np
from numpy import recfromcsv
from itertools import combinations
import os
import sys

sys.path.append(str(os.environ['QTRADE']))
from pyTrade.compute.QuantSubsystem import Quantitative
from pyTrade.utils.decorators import *

import qstkutil.tsutil as tsu


def getAllFromCSV(path='../QSData'):
        files = [f for f in os.listdir(path) if f.endswith('.csv')]
        files = [path + f for f in files]
        symbols = [os.path.splitext(f)[0] for f in files]
        return symbols, files


class Portfolio(object):
    """ Portfolio model and related utilities """
    def __init__(self, holds=None, cash=0.0):
        super(Portfolio, self).__init__()
        self.compute = Quantitative()
        self.symbols = list()
        if holds is not None:
            self.symbols.append(holds)

    def selectOnSharpeRatio(self, ls_symbols, top_n_equities=10):
        ''' Choose the best portfolio over the stock universe,
        according to their sharpe ratio'''
        #TODO: change this to a DataAccess utilitie --------------
        symbols, files = getAllFromCSV()
        datalength = len(recfromcsv(files[0])['close'])
        print('Datalength: {}'.format(datalength))
        #---------------------------------------------------------
        #Initiaing data arrays
        closes = np.recarray((datalength,), dtype=[(symbol, 'float') for symbol in symbols])
        daily_ret = np.recarray((datalength - 1,), dtype=[(symbol, 'float') for symbol in symbols])
        average_returns = np.zeros(len(files))
        return_stdev = np.zeros(len(files))
        sharpe_ratios = np.zeros(len(files))
        cumulative_returns = np.recarray((datalength - 1,), dtype=[(symbol, 'float') for symbol in symbols])

        # Here is the meat
        #TODO: data = dataobj.getData(ls_symbols)
        for i, symbol in enumerate(ls_symbols):
            if len(data) != datalength:
                continue
            print('Processing {} file'.format(file))
            closes[symbols[i]] = data['close'][::-1]
            daily_ret[symbols[i]] = compute.dailyReturns()
            # We now can compute:
            average_returns[i] = daily_ret[symbols[i]].mean()
            return_stdev[i] = daily_ret[symbols[i]].stdev()
            sharpe_ratios[i] = (average_returns[i] / return_stdev[i]) * np.sqrt(datalength)   # compare to course
            print('\tavg: {}, stdev: {}, sharpe ratio: {}'.format(average_returns[i], return_stdev[i], sharpe_ratios[i]))

        sorted_sharpe_indices = np.argsort(sharpe_ratios)[::-1][0:top_n_equities]
        #TODO: return a disct as {symbol: sharpe_ratio}, or a df with all 3 components
        return sorted_sharpe_indices

    def covarianceNpOpt(self, symbols, sorted_sharpe_indices, pf_size):
        top_n_equities = len(sorted_sharpe_indices)
        cov_data = np.zeros(datalength - 1, top_n_equities)
        for i, symbol_index in enumerate(sorted_sharpe_indices):
            cov_data[:, i] = daily_ret[symbols[symbol_index]]
        cor_mat = np.corrcoef(cov_data.transpose())
        portfolios = list(combinations(range(0, top_n_equities), pf_size))
        total_corr = [sum([cor_mat[x[0]][x[1]] for x in combinations(p, 2)]) for p in portfolios]
        best_portfolio = [symbols[sorted_sharpe_indices[i]] for i in portfolios[total_corr.index(np.nanmin(total_corr))]]
        print('Best repartition: {}'.format(best_portfolio))
        #TODO: weighed informations ?
        return best_portfolio

    def markowitzOptimization(self, dataPanel, ftarget, naLower=None, naUpper=None, naExpected=None, s_type='long'):
        '''
        See qstk documentation
        @data: pd.dataframe
        '''
        naData = self._panelToRetsArray(dataPanel)
        weight, minRet, maxRet = tsu.OptPort(naData, ftarget, naLower, naUpper, naExpected, s_type)
        return weight, minRet, maxRet    # could skip a line latter

    def getFrontier(self, panelData, lRes=100, fUpper=0.2, fLower=0.00):
        naData = self._panelToRetsArray(dataPanel)
        return tsu.getFrontier(rets, lRes, fUpper, fLower)

    def register(self, ls_symbols):
        return self.symbols.append(ls_symbols)

    def _defaultTargetReturns(self, naData):
        ''' assume target returns is average returns '''

    def pendingActions(self):
        '''
        @summary return symbols with their quantities to buy and sell, according to the optimization
        @return a dataframe, index = [quantity, order], columns=symbols
        '''

    def getComposition(self):
        '''
        @summary use cash, holds and registered symbols to compute best equities repartion
        @return a dict with symbols and quantities
        '''

    def getCompromis(self, ret_percent, risk_percent, best=None, format='raw'):
        '''
        @summary use ret and risk to retrieve the efficient frontier point associated
        @return same as getFrontier(), format parameter ?
        '''


#TODO: when forecasted prices will be available, implement tsu.optimizePortfolio
#if __name__ == '__main__':
''' Data stuff
Implement DataAccess().getChildTickets(indice)    #Or country, ...
'''
''' Compute stuff:
daily_ret = Qant.dailyRets(data['google']['close'])   # smart index handler
average_returns = np.mean(daily_ret)
return_stdev = Qant.stdev(daily_ret)
sharpe_ratios = Qant.sharpeRatio(daily_ret)
'''

''' Usage
holds = {'google' : 15, 'archos' : 56}
#NOTE: date stuff ?
p = Portfolio(holds)
p.registerSymbols()
'''
