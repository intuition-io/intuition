# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Intuition Context api
  ---------------------

  :copyright (c) 2014 Xavier Bruhiere
  :license: Apache 2.0, see LICENSE for more details.
'''

import abc
import datetime as dt
import dna.logging
import intuition.utils


def parse_storage(storage):
    tmp_uri = storage.split('?')
    path = tmp_uri[0].split('/')[1:]
    uri = tmp_uri[0].split('/')[0]

    params = {}
    if len(tmp_uri) > 1:
        tmp_params = tmp_uri[1].split('&')
        for item in tmp_params:
            if item.find('=') > 0:
                k, v = item.split('=')
                params[k] = v
            else:
                params[item] = True

    return {
        'uri': uri,
        'path': path,
        'params': params
    }


class ContextFactory():
    '''
    Context loaders give to Intuition everything it needs to know about user
    configuration. It also provides some methods to make the setup process
    easier.
    '''

    __metaclass__ = abc.ABCMeta

    def __init__(self, storage):
        self.log = dna.logging.logger(__name__)
        self.initialize(parse_storage(storage))

    def initialize(self, storage):
        ''' Users should overwrite this method '''
        pass

    @abc.abstractmethod
    def load(self, uri, path, params):
        ''' Users should overwrite this method '''
        pass

    def _normalize_dates(self, context):
        '''
        Build a timeline from given (or not) start and end dates
        '''
        if 'start' in context:
            if isinstance(context['start'], dt.date):
                context['start'] = dt.date.strftime(
                    context['start'], format='%Y-%m-%d')
        if 'end' in context:
            if isinstance(context['end'], dt.date):
                context['end'] = dt.date.strftime(
                    context['end'], format='%Y-%m-%d')

        trading_dates = intuition.utils.build_trading_timeline(
            context.pop('start', None), context.pop('end', None))

        context['index'] = trading_dates

    def _normalize_data_types(self, strategy):
        ''' some contexts only retrieves strings, giving back right type '''
        for k, v in strategy.iteritems():
            if not isinstance(v, str):
                # There is probably nothing to do
                continue
            if v == 'true':
                strategy[k] = True
            elif v == 'false' or v is None:
                strategy[k] = False
            else:
                try:
                    if v.find('.') > 0:
                        strategy[k] = float(v)
                    else:
                        strategy[k] = int(v)
                except ValueError:
                    pass

    def build(self):
        context = self.load()

        algorithm = context.pop('algorithm', {})
        manager = context.pop('manager', {})
        data = context.pop('data', {})

        if context:
            self._normalize_dates(context)

        self._normalize_data_types(algorithm)
        self._normalize_data_types(manager)
        self._normalize_data_types(data)

        strategy = {
            'algorithm': algorithm,
            'manager': manager,
            'data': data
        }

        return context, strategy
