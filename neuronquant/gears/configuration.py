import argparse
import logbook
import os
import json
import pytz
from datetime import datetime

import neuronquant.network.transport as network
from neuronquant.data.datafeed import DataFeed

log = logbook.Logger('Configuration')


class Setup(object):
    ''' Configuration object for the Trading engine'''
    def __init__(self, config_dir='', offline=False):
        '''
        Parameters
            configuration_folder: str
                default is current location for configuration files
            offline: boolean
                Can force to switch off internal server
        '''
        #NOTE timezone as parameter
        super(Setup, self).__init__()

        self.configuration_folder = config_dir if config_dir else '/'.join((os.environ['QTRADE'], 'config'))

        # Config data structures
        self.config_backtest    = dict()
        self.config_strategie   = dict()
        self.config_environment = self._inspect_environment()

        # Client for easy mysql database access
        self.datafeed = DataFeed()

        self.offline = offline
        if not offline:
            # It makes the entire simulator able to receive configuration and
            # send informations to remote users and other processes like web frontend
            self.server = network.ZMQ_Dealer(id=self.__class__.__name__)

    def _inspect_environment(self, local_file='~/.quantrade/default.json'):
        '''
        Read common user and project configuration files
        for usual environment parameters
        '''
        context = dict()
        if os.path.exists(os.path.expanduser(local_file)):
            log.info('Found local configuration file, loading {}'.format(local_file))
            context = self._read_structured_file(os.path.expanduser(local_file))
        return context

    def _read_structured_file(self, formatfile, config_folder=False, select_field=None, format='json'):
        '''
        Map well structured, i.e. common file format like key-value storage, csv, ...,  file content into a dictionnary
        '''
        if format == 'json':
            try:
                # Read given file in specified format from default or given config directory
                if config_folder:
                    content = json.load(open('/'.join([self.configuration_folder, formatfile]), 'r'))
                else:
                    content = json.load(open(formatfile, 'r'))
            except:
                log.error('** loading json configuration.')
                return dict()
        else:
            #TODO Other key-value file storage style
            raise NotImplementedError()

        # Configuration fields are likely to have several parameter categories
        # If specified, return only 'select_field' one
        return content[select_field] if select_field else content

    def parse_commandline(self):
        '''
        Read command lines arguments and map them
        to a more usuable dictionnary
        _________________________________________
        Return
            self.config_backtest: dict():
                Backtest simulator itself parameters
        '''
        log.debug('Reading commandline arguments')

        parser = argparse.ArgumentParser(description='Backtester module, the terrific financial simukation')
        parser.add_argument('-v', '--version',
                            action='version',
                            version='%(prog)s v0.8.1 Licence rien du tout', help='Print program version')
        parser.add_argument('-f', '--frequency',
                            type=str, action='store', default='daily',
                            required=False, help='(pandas) frequency in days betweend two quotes fetch')
        parser.add_argument('-a', '--algorithm',
                            action='store',
                            required=True, help='Trading algorithm to be used')
        parser.add_argument('-m', '--manager',
                            action='store',
                            required=True, help='Portfolio strategie to be used')
        parser.add_argument('-b', '--database',
                            action='store', default='test',
                            required=False, help='Table to considere in database')
        parser.add_argument('-i', '--initialcash',
                            type=float, action='store', default=100000.0,
                            required=False, help='Initial cash portfolio value')
        parser.add_argument('-t', '--tickers',
                            action='store', default='random',
                            required=False, help='target names to process')
        parser.add_argument('-s', '--start',
                            action='store', default='1/1/2006',
                            required=False, help='Start date of the backtester')
        parser.add_argument('-e', '--end',
                            action='store', default='1/12/2010',
                            required=False, help='Stop date of the backtester')
        parser.add_argument('-ex', '--exchange',
                            action='store', default='',
                            required=False, help='list of markets where trade, separated with a coma')
        parser.add_argument('-r', '--remote',
                            action='store_true',
                            help='Indicates if the program was ran manually or not')
        parser.add_argument('-l', '--live',
                            action='store_true',
                            help='makes the engine work in real-time !')
        parser.add_argument('-p', '--port',
                            action='store', default=5570,
                            required=False, help='Activates the diffusion of the universe on the network, on the port provided')
        args = parser.parse_args()

        #TODO Same as zipline in datasource, a mapping function with type and conversion function tuple
        #NOTE self.config_backtest = args.__dict__
        # For generic use, further modules will need a dictionnary of parameters, not the namespace provided by argparse
        log.debug('Mapping arguments to backtest parameters dictionnary')
        self.config_backtest = {'algorithm'   : args.algorithm,
                                'frequency'   : args.frequency,
                                'manager'     : args.manager,
                                'database'    : args.database,
                                'tickers'     : self._smart_tickers_select(args.tickers, exchange=args.exchange),
                                'start'       : self._normalize_date_format(args.start),
                                'end'         : self._normalize_date_format(args.end),
                                'live'        : args.live,
                                'port'        : args.port,
                                'exchange'    : args.exchange,
                                'cash'        : args.initialcash,
                                'remote'      : args.remote}

        return self.config_backtest

    def get_strategie_configuration(self, *args, **kwargs):
        '''
        Read localy or receive remotely
        strategie's parameters
        '''
        if kwargs.get('remote', self.config_backtest['remote']):
            # Get configuration through ZMQ socket
            self.config_strategie = self._get_remote_data(port=self.config_backtest['port'])
        else:
            log.info('Reading strategie configuration from json files')
            self.config_strategie['manager'] = \
                    self._read_structured_file('managers.json',
                                               config_folder=True,
                                               select_field=self.config_backtest['manager'])
            self.config_strategie['algorithm'] = \
                    self._read_structured_file('algorithms.json',
                                               config_folder=True,
                                               select_field=self.config_backtest['algorithm'])

        # The manager can use the same socket during simulation to emit portfolio informations
        self.config_strategie['manager']['server'] = self.server
        log.info('Configuration is Done.')

        return self.config_strategie

    def _get_remote_data(self, port, host='localhost'):
        '''
        Listen on backend ZMQ socket configuration data
        '''
        # We need data from network, start the server
        assert not self.offline
        self.server.run(host=host, port=port)

        # In remote mode, client sends missing configuration through zmq socket
        log.info('Fetching backtest configuration from client')
        msg = self.server.receive(json=True)
        log.debug('Got it !')

        # Check message format and fields
        assert isinstance(msg, dict)
        assert 'algorithm' in msg
        assert 'manager' in msg

        return msg

    def _smart_tickers_select(self, tickers_description, exchange=''):
        '''
        Take tickers string description and return
        an array of explicit and usuable symbols
        '''
        # Informations are coma separated within the string
        tickers_description = tickers_description.split(',')

        # Useful way of stocks selection in order to test algorithm strength
        if tickers_description[0] == 'random':
            # Basic check: the second argument is the the number, integer, of stocks to pick up randomly
            assert len(tickers_description) == 2
            assert int(tickers_description[1])

            # Pick up stocks on specified (or not) market exchange
            tickers_description = self.datafeed.random_stocks(int(tickers_description[1]), exchange=exchange.split(','))

        return tickers_description

    #TODO Handle in-day dates, with hours and minutes
    def _normalize_date_format(self, date):
        '''
        Dates can be defined in many ways, but zipline use
        aware datetime objects only
        __________________________________________________
        Parameters
            date: str
                String date like YYYY-MM-DD
        '''
        assert isinstance(date, str)
        return pytz.utc.localize(datetime.strptime(date, '%Y-%m-%d'))
