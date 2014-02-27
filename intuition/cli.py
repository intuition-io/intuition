# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Intuition core
  --------------

  Higher level of Intuition

  :copyright (c) 2014 Xavier Bruhiere
  :license: Apache 2.0, see LICENSE for more details.
'''

import os
import dna.logging
from intuition import __version__
from intuition.core.engine import Simulation
import intuition.core.configuration as setup

log = dna.logging.logger(__name__)


def intuition(args):
    '''________________________________________________    Setup    ____
    Setup's goal is to fill 3 dictionnaries :
      - Backtest behavior
      - Strategy parameters (algo(, source) and manager)
      - Environment (global informations like third party access)
    '''

    # Use the provided conext builder to fill the config dicts
    configuration, strategy = setup.context(args['context'])

    # Backtest or live engine.
    # Registers configuration and setups data client
    engine = Simulation()

    # Setup quotes data and financial context (location, market, ...)
    # from user parameters. Wraps _configure_context() you can use directly
    # for better understanding
    engine.configure_environment(
        configuration['index'][-1],
        configuration['exchange'])

    # Wire togetether modules and initialize them
    engine.build(args['session'], configuration['modules'], strategy)

    data = {'universe': configuration['universe'],
            'index': configuration['index']}
    data.update(strategy['data'])
    # See intuition/core/analyze.py for details of analyzes
    # which is an Analyzes object
    return engine.run(data, args['bot'])


def main():
    # General simulation behavior is defined using command line arguments
    exit_status = 0
    args = setup.parse_commandline()
    level = os.environ.get('LOG', 'warning')
    logfile = setup.logfile(args['session'])
    log_setup = dna.logging.setup(
        level=level, show_log=args['showlog'], filename=logfile)

    with log_setup.applicationbound():
        try:
            log.info('intuition v{} ready'.format(__version__),
                     level=level, bot=args['bot'],
                     context=args['context'],
                     session=args['session'])

            analyzes = intuition(args)
            analyzes.build_report(show=args['showlog'])
        except KeyboardInterrupt:
            log.info('Received SIGINT, cleaning...')
        except Exception as error:
            if level == 'debug':
                raise
            log.error('{}: {}'.format(type(error).__name__, str(error)))
            exit_status = 1

        finally:
            log.info('session ended with status {}'.format(exit_status))

    return exit_status
