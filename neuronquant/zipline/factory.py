#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2013 xavier <xavier@laptop-300E5A>
#
# Distributed under terms of the MIT license.


import pytz
from datetime import datetime

import zipline.finance.trading as trading


def create_simulation_parameters(year=2006, start=None, end=None,
                                 capital_base=float("1.0e5"),
                                 num_days=None,
                                 emission_rate='daily',
                                 data_frequency='daily'
                                 ):
    """Construct a complete environment with reasonable defaults"""
    if start is None:
        start = datetime(year, 1, 1, tzinfo=pytz.utc)
    if end is None:
        if num_days:
            trading.environment = trading.TradingEnvironment()
            start_index = trading.environment.trading_days.searchsorted(
                start)
            end = trading.environment.trading_days[start_index + num_days - 1]
        else:
            end = datetime(year, 12, 31, tzinfo=pytz.utc)
    sim_params = trading.SimulationParameters(
        period_start=start,
        period_end=end,
        capital_base=capital_base,
        emission_rate=emission_rate,
    )

    return sim_params
