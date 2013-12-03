#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

import pandas as pd
import numpy as np

from zipline.algorithm import TradingAlgorithm
from zipline.sources import DataFrameSource


class QuantitativeTrading(TradingAlgorithm):
    '''
    Intuition surcharge of main zipline class
    '''

    def __init__(self, *args, **kwargs):
        self.data_generator = DataFrameSource
        TradingAlgorithm.__init__(self, *args, **kwargs)

    def go(self, source, sim_params=None, benchmark_return_source=None):
        if isinstance(source, dict):
            source = self.data_generator(source)

        return self.run(source, sim_params, benchmark_return_source)

    def set_data_generator(self, generator_class):
        self.data_generator = generator_class
