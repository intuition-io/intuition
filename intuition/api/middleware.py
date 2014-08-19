# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Intuition middleware api
  -----------------------

  :copyright (c) 2014 Xavier Bruhiere
  :license: Apache 2.0, see LICENSE for more details.
'''

import intuition.utils as utils


# FIXME There is a semantic problem between insights.plugins and middlewares
# TODO
#   - Explicit date
#   - Specific times (started, done)
#   - Frequency (reuse Market parser)
# pylint: disable=R0921
class TimeGuard(object):
    ''' Check current date against time constraints '''

    def __init__(self, start, end, when, highfreq):
        self.highfreq = highfreq

    def __call__(self, time):
        ''' Evaluate current time '''
        if not utils.is_live and not self.highfreq:
            is_allowed = False
        else:
            is_allowed = True
        return is_allowed


class Middleware(object):
    ''' Essentially a data structure to register middlewares '''

    def __init__(self, callback, checker=None, critical=False):
        self.name = callback.__name__
        self._callback = callback
        self.args = callback.func_code.co_varnames
        self.check = checker or (lambda x: True)
        self.critical = critical

    def __call__(self, *args, **kwargs):
        ''' Safely cal the provided callback '''
        try:
            result = self._callback(*args, **kwargs)
        except Exception as error:
            result = error.message
            if self.critical:
                raise
        return result
