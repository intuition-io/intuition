#
# Copyright 2013 Xavier Bruhiere
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


import argparse
import logbook

import intuition.constants as constants
import intuition.utils.utils as utils


log = logbook.Logger('intuition.core.configuration')


def parse_commandline():
    log.debug('parsing commandline arguments')

    parser = argparse.ArgumentParser(
        description='Intuition, the terrific trading system')
    parser.add_argument('-V', '--version',
                        action='version',
                        version='%(prog)s v0.1.3 Licence Apache 2.0',
                        help='Print program version')
    parser.add_argument('-v', '--showlog',
                        action='store_true',
                        help='Print logs on stdout')
    parser.add_argument('-b', '--bot',
                        action='store_true',
                        help='Allows the algorithm to process orders')
    parser.add_argument('-c', '--context',
                        action='store', default='file::conf.yaml',
                        help='Provides the way to build context')
    parser.add_argument('-i', '--id',
                        action='store', default='gekko',
                        help='Customize the session id')
    args = parser.parse_args()

    return {
        'session': args.id,
        'context': args.context,
        'showlog': args.showlog,
        'bot': args.bot}


def _check_config(config):
    assert config
    assert ('modules' in config and 'universe' in config)
    assert 'algorithm' in config['modules']


def context(driver):
    driver = driver.split('::')
    builder_name = '{}.contexts.{}'.format(constants.MODULES_PATH, driver[0])

    build_context = utils.dynamic_import(builder_name, 'build_context')
    if not build_context:
        return {}, {'algorithm': {}, 'manager': {}}

    log.info('building context')
    config, strategy = build_context(driver[1])
    _check_config(config)

    return config, strategy
