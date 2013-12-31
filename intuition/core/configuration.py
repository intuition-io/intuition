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


log = logbook.Logger('intuition.core.configuration')


def parse_commandline():
    log.debug('parsing commandline arguments')

    parser = argparse.ArgumentParser(
        description='Intuition, the terrific trading system')
    parser.add_argument('-V', '--version',
                        action='version',
                        version='%(prog)s v0.1.3 Licence Apache 2.0',
                        help='Print program version')
    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        help='Print logs on stdout')
    parser.add_argument('-c', '--context',
                        action='store', default='file::conf.yaml',
                        help='Provides the way to build context')
    args = parser.parse_args()

    return args.context, args.verbose


def _module(name):
    ''' Return a python module from its name '''
    # why fromlist keyword:
    # http://stackoverflow.com/questions/2724260/
    # why-does-pythons-import-require-fromlist
    return __import__(name, fromlist=['whatever'])


def context(driver):
    driver = driver.split('::')
    builder_name = 'intuition.modules.contexts.{}'.format(driver[0])

    try:
        context_builder = _module(builder_name)
    except ImportError, e:
        log.error('loading context module: %s' % e)
        return {}, {'algorithm': {}, 'manager': {}}

    log.info('building context')
    return context_builder.build_context(driver[1])
