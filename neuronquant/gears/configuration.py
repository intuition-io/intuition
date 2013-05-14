import argparse
import logbook
import os
import json
import pytz
#from datetime import datetime
from dateutil.parser import parse

import neuronquant.network.transport as network
from neuronquant.data.datafeed import DataFeed

log = logbook.Logger('Configuration')


class Setup(object):
    ''' Configuration object for the Trading engine'''
    def __init__(self, config_dir=''):
        '''
        Parameters
            configuration_folder: str
                default is current location for configuration files
        '''
        #NOTE timezone as parameter
        super(Setup, self).__init__()

        self.configuration_folder = config_dir if config_dir else '/'.join((os.environ['QTRADE'], 'config'))

        # Config data structures
        self.config_backtest    = dict()
        self.config_strategy   = dict()
        self.config_environment = self._inspect_environment()

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

    #NOTE More likely to be an utils function
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
                            version='%(prog)s v0.1.3 Licence Apache 2.0', help='Print program version')
        parser.add_argument('-f', '--frequency',
                            type=str, action='store', default='daily',
                            required=False, help='(pandas) frequency in days betweend two quotes fetch')
        parser.add_argument('-a', '--algorithm',
                            action='store',
                            required=True, help='Trading algorithm to be used')
        parser.add_argument('-m', '--manager',
                            action='store', default='',
                            required=False, help='Portfolio strategie to be used')
        parser.add_argument('-d', '--database',
                            action='store', default='',
                            required=False, help='Table to considere in database')
        parser.add_argument('-i', '--initialcash',
                            type=float, action='store', default=100000.0,
                            required=False, help='Initial cash portfolio value')
        parser.add_argument('-t', '--tickers',
                            action='store', default='random',
                            required=False, help='target names to process')
        parser.add_argument('-s', '--start',
                            action='store', default='2006-01-01',
                            required=False, help='Start date of the backtester')
        parser.add_argument('-e', '--end',
                            action='store', default='2010-1-12',
                            required=False, help='Stop date of the backtester')
        parser.add_argument('-ex', '--exchange',
                            action='store', default='',
                            required=False, help='list of markets where trade, separated with a coma')
        parser.add_argument('-ll', '--loglevel',
                            action='store', default='WARNING',
                            required=False, help='File stream log level')
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
        #NOTE Algorithm should be strategie, to be consistent
        # For generic use, future modules will need a dictionnary of parameters, not the namespace provided by argparse
        log.debug('Mapping arguments to backtest parameters dictionnary')
        self.config_backtest = {'algorithm': args.algorithm,
                                'frequency': args.frequency,
                                'manager'  : args.manager,
                                'database' : args.database,
                                'tickers'  : smart_tickers_select(args.tickers, exchange=args.exchange),
                                'start'    : normalize_date_format(args.start),
                                'end'      : normalize_date_format(args.end),
                                'live'     : args.live,
                                'port'     : args.port,
                                'exchange' : args.exchange,
                                'cash'     : args.initialcash,
                                'loglevel' : args.loglevel,
                                'remote'   : args.remote}

        return self.config_backtest

    def get_strategie_configuration(self, *args, **kwargs):
        '''
        Read localy or receive remotely strategie's parameters
        '''
        # If no command line was parsed you can use manually a dict
        # for config_backtest or must specifie it outside
        if 'config_backtest' in kwargs:
            self.config_backtest = kwargs.pop('config_backtest')
        else:
            assert self.config_backtest

        if kwargs.get('remote', self.config_backtest['remote']):
            # Get configuration through ZMQ socket
            self.config_strategy = self._get_remote_data(port=kwargs.get('port', self.config_backtest['port']))

        else:
            log.info('Reading strategie configuration from json files')
            self.config_strategy['manager'] = \
                    self._read_structured_file('managers.json',
                                               config_folder=True,
                                               select_field=self.config_backtest['manager'])
            #NOTE Algorithm should be strategie, to be consistent
            self.config_strategy['algorithm'] = \
                    self._read_structured_file('strategies.json',
                                               config_folder=True,
                                               select_field=self.config_backtest['algorithm'])

        log.info('Configuration is Done.')

        return self.config_strategy

    #NOTE In this configuration remote client can't run a simulation
    #     that would use local file configurations, issue ?
    def _get_remote_data(self, port, host='localhost'):
        '''
        Listen on backend ZMQ socket configuration data
        '''
        # ZMQ Server makes the entire simulator able to receive configuration
        # and send informations to remote users and other processes like web frontend
        server = network.ZMQ_Dealer(id='Engine server')

        server.run(host=host, port=port)

        # In remote mode, client sends missing configuration through zmq socket
        log.info('Fetching backtest configuration from client')
        msg = server.receive(json=True)
        log.debug('Got it !')

        # Check message format and fields
        assert isinstance(msg, dict)
        assert 'algorithm' in msg
        assert 'manager' in msg

        # The manager can use the same socket during simulation to emit portfolio informations
        msg['manager']['server'] = server

        return msg


def smart_tickers_select(tickers_description, exchange=''):
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
        tickers_description = DataFeed().random_stocks(int(tickers_description[1]), exchange=exchange.split(','))

    return tickers_description


#TODO Handle in-day dates, with hours and minutes
def normalize_date_format(date):
    '''
    Dates can be defined in many ways, but zipline use
    aware datetime objects only. Plus, the software work
    with utc timezone so we convert it.
    __________________________________________________
    Parameters
        date: str
            String date, see dateutils module for precisions
    __________________________________________________
    Return
        datetime.datetime utc tz aware object
    '''
    assert isinstance(date, str)
    local_tz = pytz.timezone(_detect_timezone())
    local_dt = local_tz.localize(parse(date), is_dst=None)
    return local_dt.astimezone (pytz.utc)

    #locale_date = parse(date)
    #if locale_date.tzinfo is None:
        #locale_date = locale_date.replace(tzinfo=pytz.timezone(_detect_timezone()))
    ##FIXME astimezone() retieve 8 minutes from Paris timezone Oo 20 from Amsterdam WTF
    #return locale_date.astimezone(pytz.utc)


def _detect_timezone():
    '''
    Experimental and temporary (since there is a world module)
    get timezone as set by the system
    '''
    import locale
    locale_code = locale.getdefaultlocale()[0]
    return str(pytz.country_timezones[locale_code[:2]][0])
