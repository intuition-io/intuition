# -*- coding: utf-8 -*-
# vim:fenc=utf-8

'''
  Higher level of use
  -------------------

  :copyright (c) 2014 Xavier Bruhiere
  :license: Apache 2.0, see LICENSE for more details.
'''

import dna.cli
import dna.debug
import intuition.constants as constants
from intuition.engine import Core
'''
import intuition.utils as utils
import intuition.api.datafeed as datafeed
from intuition.engine import Simulation, Core
'''
import intuition.configuration as setup


class Intuition(dna.cli.Cli):
    '''
    Main simulation wrapper
    Load the configuration, run the engine and return the analysis.
    '''

    def run(self, session, context):
        self.msg('Load configuration.')
        # Use the provided context builder to load:
        #   - config: General behavior
        #   - strategy: Modules properties
        #   - market: The universe we will trade on
        with setup.LoadContext(context) as context:

            # Intuition building blocks
            modules = context.config['modules']

            self.msg('Done. Prepare Engine.')
            simulation = Core(
                context.strategy.get('cash', constants.DEFAULT_CAPITAL),
                context.config['index'],
                context.market
            )
            self.msg('\tUse {}$ on market {}.'.format(
                simulation.capital, simulation.market.raw_description)
            )

            self.msg('\tLoad Data module: HybridDataFactory.')
            data_properties = context.strategy['data']
            simulation.load_data(data_properties.get('frequency', None))
            if 'backtest' in modules:
                self.msg('\tRegister backtest data source: {}'
                         .format(modules['backtest']))
                simulation.data.add_source(
                    'backtest', modules['backtest'], **data_properties
                )
            if 'live' in modules:
                self.msg('\tRegister live data source: {}'
                         .format(modules['live']))
                simulation.data.add_source(
                    'live', modules['live'], **data_properties
                )

            if 'analyzer' in modules:
                self.msg('\tLoad custom analyzer: {}'
                         .format(modules['analyzer']))
                simulation.load_analyzer(modules['analyzer'])

            self.msg('\tLoad algorithm: {}'.format(modules['algorithm']))
            simulation.load_algorithm(
                modules['algorithm'], **context.strategy.get('algorithm', {})
            )

            self.msg('\tConfigure trading environment.')
            simulation.configure_environment()

            self.msg('\nSetup completed, processing simulation ...')
            self.msg('\t{} -> {} ({})'.format(
                str(simulation.data.start),
                str(simulation.data.end),
                simulation.market.timezone)
            )
            analysis = simulation(session)
            self.success('Terminated successfully.')
            self.msg('\nAnalysis\n', underline=True, bold=True)
            self.msg(dna.debug.emphasis(analysis.report(), align=True),
                     bold=True)
            self.msg('\n')
            return 0
