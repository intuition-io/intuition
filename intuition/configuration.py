# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Intuition configuration
  -----------------------

  Configure intuition at launch time

  :copyright (c) 2014 Xavier Bruhiere
  :license: Apache 2.0, see LICENSE for more details.
'''

import pytz
from schematics.types import StringType, URLType
import dna.logging
import dna.utils
import intuition.constants
import intuition.utils as utils
import intuition.data.universe as universe
from intuition.errors import InvalidConfiguration

log = dna.logging.logger(__name__)


class Context(object):
    ''' Data Structure '''
    def __init__(self, initial_values):
        self.__dict__ = initial_values

    def __getitem__(self, name):
        return self.__dict__[name]


class LoadContext(object):
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

        # Trader identity, optional and printed for development for now
        trader = config.pop('author', None)
        if isinstance(trader, dict):
            log.info('Trader identity', **trader)

        # TODO Validate strategy as well
        self._validate(config)

        # From a human input (forex,4), setup a complete market structure
        market_ = universe.Market()
        market_.parse_universe_description(config.pop('universe'))

        log.info('Context successfully loaded')
        return Context({
            'config': config, 'strategy': strategy, 'market': market_
        })

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
