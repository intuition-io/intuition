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
    '''
    Main simulation wrapper
    Load the configuration, run the engine and return the analyze.
    '''

    # Use the provided context builder to load:
    #   - config: General behavior
    #   - strategy: Modules properties
    #   - market: The universe we will trade on
    with setup.Context(args['context']) as context:

        # Backtest or live engine.
        # Registers configuration and setups data client
        simulation = Simulation()

        # Intuition building blocks
        modules = context['config']['modules']

        # Prepare benchmark, timezone, trading calendar
        simulation.configure_environment(
            context['config']['index'][-1],
            context['market'].benchmark,
            context['market'].timezone
        )

        # Wire togetether modules and initialize them
        simulation.build(args['session'],
                         modules,
                         context['strategy'])

        # Build data generator
        # NOTE How can I use several sources ?
        data = {
            'universe': context['market'],
            'index': context['config']['index']
        }
        # Add user settings
        data.update(context['strategy']['data'])
        # Load backtest and / or live module(s)
        if 'backtest' in modules:
            data['backtest'] = utils.intuition_module(modules['backtest'])
        if 'live' in modules:
            data['live'] = utils.intuition_module(modules['live'])

        # Run the simulation and return an intuition.core.analyzes object
        return simulation(datafeed.HybridDataFactory(**data), args['bot'])


def main():
    # General simulation behavior is defined using command line arguments
    exit_status = 0
    args = setup.parse_commandline()
    loglevel = os.environ.get('LOG', 'warning')
    logfile = setup.logfile(args['session'])
    # Setup structured logs with file and stdout support
    log_setup = dna.logging.setup(
        level=loglevel, show_log=args['showlog'], filename=logfile)

    with log_setup.applicationbound():
        try:
            log.info('intuition v{} ready'.format(__version__),
                     level=loglevel, bot=args['bot'],
                     context=args['context'],
                     session=args['session'])

            analyzes = intuition(args)
            analyzes.build_report(show=args['showlog'])
        except KeyboardInterrupt:
            log.info('Received SIGINT, cleaning...')
        except Exception as error:
            if loglevel == 'debug':
                raise
            log.error('{}: {}'.format(type(error).__name__, str(error)))
            exit_status = 1

        finally:
            log.info('session ended with status {}'.format(exit_status))

    return exit_status
