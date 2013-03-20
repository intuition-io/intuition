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
Tests for the forex datasource
'''

from unittest import TestCase
from nose.tools import timed

from neuronquant.utils.test_utils import (
        setup_logger,
        teardown_logger
)

import neuronquant.gears.configuration as configuration

DEFAULT_TIMEOUT = 15
EXTENDED_TIMEOUT = 90


class TestSetup(TestCase):
    '''
    Forex access through TrueFX provider
    !! Beware that truefx server will return empty array
    if currencies were not updated since last call
    '''
    def setUp(self):
        setup_logger(self)
        self.config = configuration.Setup()

    def tearDown(self):
        teardown_logger(self)

    def test_get_local_strategie_configuration(self):
        ''' Fill a strategie dictionnary with manager and alogrithm fields
        from local configuration file'''
        pass
