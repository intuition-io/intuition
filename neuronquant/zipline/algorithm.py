#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2013 xavier <xavier@laptop-300E5A>
#
# Distributed under terms of the MIT license.

import pandas as pd
import numpy as np

from zipline.algorithm import TradingAlgorithm
from zipline.sources import DataFrameSource


class QuantitativeTrading(TradingAlgorithm):
    '''
    QuanTrade customisation of main zipline class
    '''

    def __init__(self, *args, **kwargs):
        self.data_generator = DataFrameSource
        TradingAlgorithm.__init__(self, *args, **kwargs)

    def go(self, source, sim_params=None, benchmark_return_source=None):
        if isinstance(source, dict):
            source = self.data_generator(source)

        return self.run(source, sim_params, benchmark_return_source)

    #TODO Ok to be removed, cum_perfs are now available with self.risk_report
    def _create_daily_stats(self, perfs):
        # create daily and cumulative stats dataframe
        daily_perfs = []
        cum_perfs = []
        # TODO: the loop here could overwrite expected properties
        # of daily_perf. Could potentially raise or log a
        # warning.
        for perf in perfs:
            if 'daily_perf' in perf:

                perf['daily_perf'].update(
                    perf['daily_perf'].pop('recorded_vars')
                )
                daily_perfs.append(perf['daily_perf'])
            else:
                cum_perfs.append(perf)

        daily_dts = [np.datetime64(perf['period_close'], utc=True)
                     for perf in daily_perfs]
        daily_stats = pd.DataFrame(daily_perfs, index=daily_dts)

        #TODO Use examples from analyzes to arrange it
        return daily_stats, cum_perfs[-1]

    def set_data_generator(self, generator_class):
        self.data_generator = generator_class
