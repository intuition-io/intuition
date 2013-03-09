#
# Copyright 2012 Xavier Bruhiere
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


'''
Tests for the neuronquant.ai package
'''

from unittest import TestCase
from nose.tools import timed

from neuronquant.utils.test_utils import (
        setup_logger,
        teardown_logger
)

from neuronquant.ai.portfolio import PortfolioManager

DEFAULT_TIMEOUT = 15
EXTENDED_TIMEOUT = 90


class TestPortfolio(TestCase):
    def setUp(self):
        setup_logger(self)
        parameters = {}
        self.manager = PortfolioManager(parameters)

    def tearDown(self):
        teardown_logger(self)

    #NOTE I need a portfolio object
    @timed(DEFAULT_TIMEOUT)
    def update_portfolio_universe(self):
        pass

    def signals_manipulation(self):
        pass

    def set_portfolio_properties(self):
        self.manager.setup_strategie({'test_max_weigth': 0.56, 'test_frequency': 45})
        assert self.manager._optimizer_parameters['test_max_weigth'] == 0.56
        assert self.manager._optimizer_parameters['test_frequency'] == 45
