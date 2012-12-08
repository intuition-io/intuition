#!/usr/bin/python
# -*- coding: utf8 -*-

# Logger class (obviously...)
from Utilities import LogSubSystem
from Utilities import DatabaseSubSystem

# For mathematical stuff, data manipulation...
from pandas import Index, DataFrame
# Statsmodels has ols too, benchamark needed
from pandas import ols


'''---------------------------------------------------------------------------------------
Quant
---------------------------------------------------------------------------------------'''
class Graph(object):
  ''' Trade qunatitativ module 
  an instanciation work on a data set specified while initializing'''
  def __init__(self, quotes, logger=None):
    if logger == None:
      self._logger = LogSubSystem('Computer', "debug").getLog()
    else:
      self._logger = logger
    self._quotes = data
    #TODO: initialize database 

    
'''---------------------------------------------------------------------------------------
Usage Exemple
---------------------------------------------------------------------------------------'''
'''
if __name__ == '__main__':
'''

