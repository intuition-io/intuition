# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Analyzis API
  ------------

  :copyright (c) 2014 Xavier Bruhiere
  :license: Apache 2.0, see LICENSE for more details.
'''

import abc


class AnalysisFactory(object):
    '''
    This object grabs backtest statistics to produce comprehensive reports
    '''

    __metaclass__ = abc.ABCMeta

    # NOTE This method should never be overwritten
    def __init__(self, stats, risks):
        self.stats = stats
        # NOTE risks object is awesome but lot of remaining useless infos
        self.risks = risks

    @abc.abstractmethod
    def report(self):
        ''' This method should produce a dict summary of performances '''
        pass


# pylint: disable=R0921
class Basic(AnalysisFactory):
    ''' Leverage risks built-in method to produce a simple overview '''

    def report(self):
        return self.risks.to_dict()
