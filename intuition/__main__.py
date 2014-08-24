#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Intuition app entry point
  --------------------------

  :copyright (c) 2014 Xavier Bruhiere
  :license: Apache 2.0, see LICENSE for more details.
'''

import os
import sys
import click
import dna.logging
import intuition.cli as cli
from intuition import __version__
import intuition.constants as constants

log = dna.logging.logger(__name__)


def logfile(session_id):
    # Create a special file for the session, with a fallback in /tmp
    log_path = os.path.expanduser('~/.intuition/logs')
    log_path = log_path if os.path.exists(log_path) \
        else constants.DEFAULT_LOGPATH
    return '{}/{}.log'.format(log_path, session_id)


def validate_log_level(ctx, param, value):
    if value not in constants.LOGBOOK_LEVELS:
        raise click.BadParameter('Invalid log level: {}'.format(value))
    return value


# TODO Add args checkers
# TODO Check setup.py integration
@click.command()
@click.version_option(version=__version__, prog_name='intuition')
@click.option('--id', 'session', default='gekko', help='Customize session id')
@click.option('-c', '--context', required=True, help='How to build context')
@click.option('-o', '--log-output', help='stdout or logfile')
@click.option('-l', '--log-level', default='info', callback=validate_log_level)
def main(**kwargs):
    ''' Trading kit for hackers '''
    app = cli.Intuition('Intuition - Trading kit for hackers')

    app.msg('Setup structured logs handler.')
    log_output = kwargs.pop('log_output') or logfile(kwargs['session'])
    log_setup = dna.logging.setup(
        level=kwargs.pop('log_level'), output=log_output
    )
    with log_setup.applicationbound():
        app.msg('Safely call main routine.')
        status = app(**kwargs)
        log.info(status)
        return 0 if status is None else 1


if __name__ == '__main__':
    sys.exit(main())
