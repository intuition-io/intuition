#!/usr/bin/python
# encoding: utf-8
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

import neuronquant.utils.world as world
import neuronquant.tmpdata.remote as remote


class DataBot(object):
    '''
    Main interface for financial data, doesn't care about sources.  Sub-class
    work with UTC configuration, here are handle suitable conversions
    and pretty presentations.
    '''
    def __init__(self, country_code=None):
        '''
        Parameters
            country_code: str
                This information is used to setup International object
                and get the right local conventions for lang, dates and currencies
                None will stand for 'fr'
        '''
        self.location = world.International(country_code)
