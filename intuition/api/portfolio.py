# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Intuition Portfolio manager api
  -------------------------------

  Portfolio manager factory. Assets allocation strategies should inherit from
  this class.

  :copyright (c) 2014 Xavier Bruhiere
  :license: Apache 2.0, see LICENSE for more details.
'''


import abc
import dna.logging
import intuition.data.remote as remote
from intuition.errors import PortfolioOptimizationFailed


class PortfolioFactory():
    '''
    Manages portfolio during simulation, and stays aware of the situation
    through the update() method.

    User strategies call it with a dictionnnary of detected opportunities (i.e.
    buy or sell signals).  Then the optimize function computes assets
    allocation, returning a dictionnary of symbols with their weigths or amount
    to reallocate.

    {'buy': zipline.Positions}    __________________________      _____________
    signals                   --> |                         | -> |            |
                                  | trade_signals_handler() |    | optimize() |
    orders  {'google': 34}    <-- |_________________________| <- |____________|

    This is abstract class, inheretid class will eventally overwrite optmize()
    to expose their own asset allocation strategy.
    '''

    __metaclass__ = abc.ABCMeta

    # Zipline portfolio object, updated during simulation with self.date
    portfolio = None
    perfs = None
    date = None

    #TODO Add in the constructor or setup parameters some general settings like
    #     maximum weights, positions, frequency, ...
    #TODO Remove stocks with 0 to allocate
    #NOTE Regarding portfolio constraints: from a set of user-defined
    # parameters, a unique set should be constructed. Then the solution
    # provided by optimize function would have to be a subset of it. (classic
    # mathematical solution) Finally it should be defined how to handle
    # non-correct solutions
    def __init__(self, configuration):
        '''
        Parameters
            configuration : dict
                Named parameters used either for general portfolio settings
                (server and constraints), and for user optimizer function
        '''
        # Portfolio owner, mainly used for database saving and client
        # communication
        self.log = dna.logging.logger(__name__)

        # Other parameters are used in user's optimize() method
        self._optimizer_parameters = configuration

        # In case user optimization would need to retrieve more data
        self.data = remote.Data()

        self.initialize(configuration)

    def initialize(self, configuration):
        ''' Users should overwrite this method '''
        pass

    @abc.abstractmethod
    def optimize(self, date, to_buy, to_sell, parameters):
        ''' Users should overwrite this method '''
        pass

    def update(self, portfolio, date, perfs=None):
        '''
        Actualizes the portfolio universe with the alog state
        '''
        # Make the manager aware of current simulation
        self.portfolio = portfolio
        self.perfs = perfs
        self.date = date

    def trade_signals_handler(self, signals):
        '''
        Process buy and sell signals from the simulation
        '''
        alloc = {}

        if signals['buy'] or signals['sell']:
            # Compute the optimal portfolio allocation,
            # Using user defined function
            try:
                alloc, e_ret, e_risk = self.optimize(
                    self.date, signals['buy'], signals['sell'],
                    self._optimizer_parameters)
            except Exception, error:
                raise PortfolioOptimizationFailed(
                    reason=error, date=self.date, data=signals)

        return alloc

    def advise(self, **kwargs):
        '''
        General parameters or user settings
        (maw_weigth, max_assets, max_frequency, commission cost)
        '''
        for name, value in kwargs.iteritems():
            self._optimizer_parameters[name] = value
