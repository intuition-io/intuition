# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Intuition specific errors
  -------------------------

  :copyright (c) 2014 Xavier Bruhiere
  :license: Apache 2.0, see LICENSE for more details.
'''


import dna.errors


class InvalidConfiguration(dna.errors.FactoryError):
    msg = "invalid configuration: {config} ({module})"


class PortfolioOptimizationFailed(dna.errors.FactoryError):
    msg = """
[{date}] \
Portfolio optimization failed: {reason}, \
processing {data}
""".strip()


class AlgorithmEventFailed(dna.errors.FactoryError):
    msg = """
[{date}] \
algorithm event failed: {reason}, \
processing {data}
""".strip()
