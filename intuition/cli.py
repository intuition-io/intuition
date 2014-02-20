# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Intuition core
  --------------

  Higher level of intuition use

  :copyright (c) 2014 Xavier Bruhiere
  :license: Apache 2.0, see LICENSE for more details.
'''

import os
import dna.logging
from intuition import __version__
from intuition.core.engine import Simulation
from intuition.data.data import Exchanges
import intuition.core.configuration as setup

log = dna.logging.logger(__name__)


def show_perfs(cash, bm_symbol, analyzes):
    # Get daily, cumulative and not, returns of portfolio and benchmark
    returns_df = analyzes.get_returns(benchmark=bm_symbol)

    perfs = analyzes.overall_metrics('one_month')

    orders = 0
    for order in analyzes.results.orders:
        orders += len(order)

    final_value = analyzes.results.portfolio_value[-1]
    gain = final_value - cash
    pf_gain_perc = returns_df['algo_c_return'][-1] * 100.0
    bm_gain_perc = returns_df['benchmark_c_return'][-1] * 100.0
    pnl_mean = analyzes.results.pnl.mean()
    pnl_std = analyzes.results.pnl.std()

    print('\n ======================  Results  ==\n')
    log.info('Final value: {} $'.format(final_value))
    log.info('Processed {} orders'.format(orders))
    log.info('Perf: {:.2f}% / {:.2f}%\tGain: {} $'
             .format(pf_gain_perc, bm_gain_perc, gain))
    log.info('Achieved on average a pnl of {:.2f} with {:.2f} of deviation'
             .format(pnl_mean, pnl_std))
    for k, v in perfs.iteritems():
        log.info('{}: {}'.format(k, v))
    print('\n ===================================\n')


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
        configuration['index'][-1], configuration['exchange'])

    # Wire togetether modules and initialize them
    engine.build(args['session'], configuration['modules'], strategy)

    data = {'universe': configuration['universe'],
            'index': configuration['index']}
    data.update(strategy['data'])
    # See intuition/core/analyze.py for details of analyzes
    # which is an Analyzes object
    analyzes = engine.run(data, args['bot'])

    bm_symbol = Exchanges[configuration['exchange']]['symbol']
    show_perfs(strategy['manager']['cash'], bm_symbol, analyzes)


def main():
    # General simulation behavior is defined using command line arguments
    exit_status = 0
    args = setup.parse_commandline()
    level = os.environ.get('LOG', 'warning')
    log_setup = dna.logging.setup(level=level, show_log=args['showlog'])

    with log_setup.applicationbound():
        try:
            log.info('intuition v{} ready'.format(__version__),
                     level=level, bot=args['bot'],
                     context=args['context'],
                     session=args['session'])

            intuition(args)
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
