# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Intuition configuration
  -----------------------

  Configure intuition at launch time

  :copyright (c) 2014 Xavier Bruhiere
  :license: Apache 2.0, see LICENSE for more details.
'''

import os
import argparse
import dna.logging
import dna.utils
from intuition import __version__, __licence__
import intuition.constants
import intuition.utils as utils

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
    driver = driver.split('://')
    context_builder = utils.intuition_module(driver[0])

    log.info('building context', driver=driver[0], data=driver[1])
    return context_builder(driver[1]).build(validate=True)


def logfile(session_id):
    log_path = os.path.expanduser('~/.intuition/logs')
    log_path = log_path if os.path.exists(log_path) \
        else intuition.constants.DEFAULT_LOGPATH
    return '{}/{}.log'.format(log_path, session_id)
