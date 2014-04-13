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
    msg = "invalid configuration: {reason} ({config})"


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


class LoadDataFailed(dna.errors.FactoryError):
    msg = "Failed to load data for {sids}: {reason}"


class LoadMarketSchemeFailed(dna.errors.FactoryError):
    msg = "Failed to load market scheme: {reason}"


class LoadContextFailed(dna.errors.FactoryError):
    msg = "Unable to load data from {driver}: {reason}"


class ExchangeIsClosed(dna.errors.FactoryError):
    msg = "{exchange} is closed during {dates}"


class InvalidEngine(dna.errors.FactoryError):
    msg = "Invalid engine {id}: {reason}"


class InvalidDatafeed(dna.errors.FactoryError):
    msg = "Invalid datafeed setup: {reason}"
