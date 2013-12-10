#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8


from zipline.algorithm import TradingAlgorithm
from zipline.sources import DataFrameSource
from zipline.protocol import Event
import zipline.protocol


class TradingFactory(TradingAlgorithm):
    '''
    Intuition surcharge of main zipline class
    '''
    is_live = False

    def __init__(self, *args, **kwargs):
        self.data_generator = DataFrameSource
        TradingAlgorithm.__init__(self, *args, **kwargs)

    def go(self, source, sim_params=None, benchmark_return_source=None):
        '''
        if self.is_live:
            benchmark_return_source = [
                Event({'dt': dt,
                       'returns': 0.0,
                       'type': zipline.protocol.DATASOURCE_TYPE.BENCHMARK,
                       'source_id': 'benchmarks'})
                for dt in source['index']
                if dt.date() >= sim_params.period_start.date()
                and dt.date() <= sim_params.period_end.date()]
          '''

        if isinstance(source, dict):
            source = self.data_generator(source)

        return self.run(source, sim_params, benchmark_return_source)

    def set_data_generator(self, generator_class):
        self.data_generator = generator_class
