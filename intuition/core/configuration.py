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
import pytz
from schematics.types import StringType, URLType
import dna.logging
import dna.utils
from intuition import __version__, __licence__
import intuition.constants
import intuition.utils as utils
import intuition.data.universe as universe
from intuition.errors import InvalidConfiguration

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

    # Dict will be more generic to process than args namespace
    return {
        'session': args.id,
        'context': args.context,
        'showlog': args.showlog,
        'bot': args.bot
    }


class Context(object):
    ''' Load and control configuration '''

    def __init__(self, access):
        # Hold infos to reach the config formatted like an url path
        # <path.to.module>://<ip>:<port>/<access/...?<key>=<value>...
        StringType(regex='.*://\w').validate(access)
        self._ctx_module = access.split('://')[0]
        self._ctx_infos = access.split('://')[1]
        URLType().validate('http://{}'.format(self._ctx_infos))

    def __enter__(self):
        # Use the given context module to grab configuration
        Loader = utils.intuition_module(self._ctx_module)
        log.info('building context',
                 driver=self._ctx_module, data=self._ctx_infos)
        config, strategy = Loader(self._ctx_infos).build()

        # TODO Validate strategy as well
        self._validate(config)

        # From a human input (forex,4), setup a complete market structure
        market_ = universe.Market()
        market_.parse_universe_description(config.pop('universe'))

        return {'config': config, 'strategy': strategy, 'market': market_}

    def __exit__(self, type, value, traceback):
        pass

    def _validate(self, config):
        log.info('validating configuration', config=config)
        try:
            # Check if needed informations are here
            assert intuition.constants.CONFIG_SCHEMA.validate(config)
            # Index Check
            assert config['index'].size, 'No trading timeline'
            assert (config['index'].tzinfo == pytz.utc), 'Invalid timezone'
        except Exception as error:
            raise InvalidConfiguration(config=config, reason=error)


def logfile(session_id):
    # Create a special file for the session, with a fallback in /tmp
    log_path = os.path.expanduser('~/.intuition/logs')
    log_path = log_path if os.path.exists(log_path) \
        else intuition.constants.DEFAULT_LOGPATH
    return '{}/{}.log'.format(log_path, session_id)
