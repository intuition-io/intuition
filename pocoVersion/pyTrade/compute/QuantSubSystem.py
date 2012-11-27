#!/usr/bin/python
# -*- coding: utf8 -*-

# Logger class (obviously...)
from Utilities import LogSubSystem
from Utilities import DatabaseSubSystem

# For mathematical stuff, data manipulation...
import numpy as np


'''---------------------------------------------------------------------------------------
Quant
---------------------------------------------------------------------------------------'''
class Quantitative:
  ''' Trade qunatitativ module 
  an instanciation work on a data set specified while initializing'''
  def __init__(self, data, logger=None):
    if logger == None:
      logSys = LogSubSystem(__name__, "debug")
      self._logger = logSys.getLog()
    else:
      self._logger = logger
    self._data = data
    #TODO: initialize database 

  def variation(self, period=0, start_date=0):
    ''' Day variation if nothing specified
    from startDate and for period otherwize '''
    #TODO: Find a way to manipulate dates
    if period + start_date == 0:  # Wants day variation
      self._logger.debug("Day variation")
      return ((self._data[self._data.shape[0]-1, 4] - self._data[0, 4]) / self._data[0, 4]) * 100
    elif period > 0 and start_date > 0:  # Variation between two dates
      self._logger.debug("Variation between two dates")
      return 1
    elif period > 0 and start_date == 0:  # Want variation from now to start_date
      self._logger.debug("Variation from now to date")
      return 2

  #TODO: updateDB, every class has this method, factorisation ? shared memory map to synchronize

'''---------------------------------------------------------------------------------------
Usage Exemple
---------------------------------------------------------------------------------------'''
'''
if __name__ == '__main__':
'''

