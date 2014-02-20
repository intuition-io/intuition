# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Intuition configuration
  -----------------------

  Configure intuition at launch time

  :copyright (c) 2014 Xavier Bruhiere
  :license: Apache 2.0, see LICENSE for more details.
'''

import argparse
import dna.logging
import dna.utils
from intuition import __version__, __licence__
import intuition.constants as constants
from intuition.errors import InvalidConfiguration
from intuition.constants import CONFIG_SCHEMA

log = dna.logging.logger(__name__)


def parse_commandline():
    parser = argparse.ArgumentParser(
        description='Intuition, the terrific trading system')
    parser.add_argument('-V', '--version',
                        action='version',
                        version='%(prog)s v{} Licence {}'.format(
                            __version__, __licence__),
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


def context(driver):
    #TODO Check driver syntax
    driver = driver.split('::')
    #TODO No use of environment, it breaks how other modules are found
    builder_name = '{}.contexts.{}'.format(constants.MODULES_PATH, driver[0])

    build_context = dna.utils.dynamic_import(builder_name, 'build_context')

    log.info('building context')
    config, strategy = build_context(driver[1])

    log.info('validating configuration')
    try:
        assert CONFIG_SCHEMA.validate(config)
    except:
        raise InvalidConfiguration(config=config, module=builder_name)

    return config, strategy
