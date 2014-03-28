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
import intuition.utils as utils
import intuition.api.datafeed as datafeed
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

    # Use the provided context builder to fill the config dicts
    #configuration, strategy = setup.context(args['context'])
    with setup.Context(args['context']) as context:

        # Backtest or live engine.
        # Registers configuration and setups data client
        simulation = Simulation()

        # Setup quotes data and financial context (location, market, ...) from
        # user parameters. Wraps _configure_context() you can use directly for
        # better understanding
        simulation.configure_environment(
            context['config']['index'][-1],
            context['market'])

        # Wire togetether modules and initialize them
        simulation.build(args['session'],
                         context['config']['modules'],
                         context['strategy'])

        # Build data generator
        #TODO How can I use several sources ?
        data = {'universe': context['market'],
                'index': context['config']['index']}
        data.update(context['strategy']['data'])
        if 'backtest' in context['config']['modules']:
            data['backtest'] = utils.intuition_module(
                context['config']['modules']['backtest'])
        if 'live' in context['config']['modules']:
            data['live'] = utils.intuition_module(
                context['config']['modules']['live'])

        return simulation(datafeed.HybridDataFactory(**data), args['bot'])


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
