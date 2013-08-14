# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2013 xavier <xavier@laptop-300E5A>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os
import json
import logbook
from datetime import datetime
import xmlrpclib
log = logbook.Logger('Grid::Main')

from gryd.utils.signals import SignalManager
from gryd.utils.utils import get_local_ip, complete_configuration
from gryd.dashboard import Dashboard
from gryd.dashboard import LogIO
import gryd.fabfile as fab

from IPython.parallel import Client, error

from fabric.api import (
    env, execute
)


CONFIG_PATH = os.path.expanduser('~/.quantrade/default.json')
TASKS_PATH = os.path.expanduser('~/dev/projects/ppQuanTrade/config/plugins.json')
REPORT_PATH = os.path.expanduser('~/.quantrade/report')
ROOT_NAME = 'Xavier'
ROOT_PORT = 5555


class Drone(object):
    '''
    A drone is a remote/local engine you can run tasks on
    '''

    def __init__(self, engine, configuration, id=0):
        self.id = id
        self.port = ROOT_PORT + id
        self.engine = engine
        self.process = None
        self.is_running = False
        self.ip = engine.apply_sync(get_local_ip)

        self.status = engine.queue_status()
        assert ((self.status['queue'] == 0) and (self.status['tasks'] == 0))

        self.configuration, self.name = self._inspect(configuration)

        log.debug('Using new drone on {} With configuration:\n{}'.format(
            self.ip, configuration))

    def _inspect(self, configuration):
        #NOTE python use pointers, will it work without returning anything ?
        configuration = self._sanitize_format(configuration)

        name = '-'.join((str(self.id),
                         ROOT_NAME,
                         configuration['configuration']['exchange'],
                         configuration['configuration']['algorithm'],
                         configuration['configuration']['manager']))

        configuration['strategie']['manager']['name'] = name
        configuration['configuration']['logfile'] = name + '.log'
        configuration['configuration']['port'] = self.port

        return configuration, name

    def _sanitize_format(self, config):
        '''
        Configuration can be submitted in 2 ways:
            - In a complete format, everything provided
            - As a dictionnary that lists modifications from a default config
        '''
        if not ['configuration', 'strategie'] == config.keys():
            # Second option
            config = complete_configuration(root_configuration, config)

        return config

    def run(self, function):
        '''
        Use Ipython remote ipengine to execute the given function
        '''
        # Run remote process
        log.info('Running trade system on node %d::%s (%s)'
                 % (self.id, self.ip, self.name))
        self.process = self.engine.apply_async(function, self.configuration)
        self.is_running = True

    def is_done(self):
        if self.process:
            return self.process.ready()
        return False

    def finalize(self, report=''):
        self.is_running = False
        msg = '[{}] Done with status: {}'
        log.info(msg.format(self.name, self.process.successful()))
        try:
            log.info(self.process.get())
        except error.RemoteError, e:
            log.error('Process {} ended with an exception: {}'.format(id, e))
            if report:
                with open('.'.join((report, self.ip, 'md')), "a") as f:
                    f.write('[{}] {} - {}\n'.format(
                        datetime.now(), self.name, e))

    def __del__(self):
        log.info('Shutting down drone {}::{}'.format(self.ip, self.name))
        #FIXME kill indeed but Client() is complaining not finding it after)
        #self.engine.shutdown()
        #self.engine.kill()


class Node(object):
    '''
    A node is a physical machine, part of the cluster It runs glances, rest
    servers, drones and is optimized for quantrade execution
    '''

    def __init__(self, ip, monitored=False, restful=False):
        self.ip = ip
        self.drones = {}
        self.tasks = []

        self.glances_port = 61209
        self.is_monitored = monitored
        self.is_restful = restful
        self._setup(monitored, restful)

    def _setup(self, monitored, restful):
        if restful:
            log.info('Activating remote rest_server')
            execute(fab.activate_restserver, host=self.ip)

        if monitored:
            log.info('Activating remote glances monitoring')
            execute(fab.activate_monitoring, host=self.ip)

            self.monitor = xmlrpclib.ServerProxy(
                'http://{}:{}'.format(self.ip, self.glances_port))

    def register_drone(self, id, engine):
        '''
        Receive and store an engine object and create a drone one after
        fetching its configuration
        '''
        if not len(self.tasks):
            log.info('No pending tasks, fetching new availables')
            self._fetch_tasks(TASKS_PATH)

        log.info('{} task(s) left'.format(len(self.tasks)))

        log.info('Registering {}e drone on {}'.format(
            len(self.drones), self.ip))
        self.drones[id] = Drone(engine, self.tasks.pop(0), id)

    def _fetch_tasks(self, remote_path):
        '''
        When new drones are ready it means you can run tasks configured where
        they come from
        '''
        new_tasks = execute(fab.load_remote_file, remote_path, host=self.ip)
        assert self.ip in new_tasks
        self.tasks.extend(new_tasks[self.ip]['components'])

    def inspect_armada(self, drone_id=None):
        ids = self.drones.keys()
        #for id, drone in self.drones.iteritems():
        for id in ids:
            if drone_id and (id != drone_id):
                continue
            if self.drones[id].is_done():
                self.drones[id].finalize(report=REPORT_PATH)
                del self.drones[id]


class Grid(object):
    '''
    Responsible to run QuanTrade runtime and communicate with drones

    It forks:
        - log.io for logs aggregation
        - dashboards for trading purpose
    And dynamically:
        - Remote rest_services for database wrappers
        - Drones to process remote calls
        - Glances servers and clients for ressources monitoring

    It basically waits for new tasks to pop (ie remote engines to appear), and
    fork trading processes on them according to their associated configuration.
    It can as well create by itself remote/local drones for classic cluster
    purpose.

    The object can be configured through ~/.quantrade/default.json.
    '''

    def __init__(self, configuration_path=CONFIG_PATH):
        log.info('Running Grid master, stop it with CTRL-C')

        # CTRL-C interception
        SignalManager()

        # Setup object configuration
        self._configure(configuration_path)

        # Team_dashboard web graphs
        self.dashboard = Dashboard()
        # Logs monitoring
        self.logio = LogIO(self.configuration['nodes'])

        # Nodes are physical machines of the cluster
        self.nodes = {ip: Node(ip, self.configuration['monitored'],
                               self.configuration['restful'])
                      for ip in self.configuration['nodes']}

        self.processed_engines = []

    def _configure(self, configuration_path):
        '''
        Read and set configuration
        '''
        self.configuration = json.load(open(configuration_path, 'r'))['grid']
        #http://docs.fabfile.org/en/1.4.3/usage/env.html#full-list-of-env-vars
        #env.forward_agent = True
        #env.key_filename = [""]
        env.user = self.configuration['name']
        env.password = self.configuration['password']
        env.hosts = self.configuration['nodes']
        env.roledefs = {
            'local': ['127.0.0.1'],
            'controller': self.configuration['controller'],
            'nodes': self.configuration['nodes']
        }

    def deploy(self):
        '''
        Set up local ipcontroller
        '''
        log.info('Deploying grid trade-system')
        log.info('Activating local ipcontroller')
        execute(fab.activate_controller)

        # Main interface to drones
        self.engines = Client()

    def _is_idle(self, state):
        '''
        Check if there is pending tasks to do
        '''
        if 'queue' in state:
            return not state['queue']

        # Else, no informations to answer
        return None

    def detect_drones(self):
        new_engines = []
        engines_status = self.engines.queue_status()
        #NOTE what is the use of status['unassigned'] ?
        for key, state in engines_status.iteritems():
            if key == 'unassigned':
                continue
            if (self._is_idle(state)
                    and key not in self.processed_engines):
                self.processed_engines.append(key)
                new_engines.append(self.engines[key])

        self._dispatch_engines(new_engines)
        return len(new_engines)

    def _dispatch_engines(self, engines):
        for engine in engines:
            ip = engine.apply_sync(get_local_ip)
            log.info('New engine detected on {}'.format(ip))
            if ip not in self.nodes:
                log.info('New node connected')
                self.nodes[ip] = Node(ip, self.configuration['monitored'],
                                      self.configuration['restful'])

            self.nodes[ip].register_drone(engine.targets, engine)

            drone_name = self.nodes[ip].drones[engine.targets].name
            self.dashboard.add_description(remote_ip=ip, portfolio=drone_name)
            self.logio.add_description(drone_name, remote_ip=ip)

            log.info('Drone registered')

    def process(self, function, node_ip=None, drone_id=None):
        '''
        Process pending tasks on available, and eventually provided, drones
        '''
        processed_nodes = self.nodes.values()
        for node in processed_nodes:
            processed_drones = node.drones.values()
            #FIXME use self.engines.shutdown([1, 3]) insteand of
            #non-functionnal drone.shutdown
            node.inspect_armada()
            for drone in processed_drones:
                drone.run(function)

    def fireup_dashboards(self):
        if self.configuration['logserver']:
            self.logio.build()
            self.logio.run()
            log.notice('Log.io available at http://192.168.0.12:28778')

        if self.configuration['dashboard']:
            self.dashboard.build()
            self.dashboard.run(public_ip=False)
            log.notice('Dashboard available at http://192.168.0.12:4000')


#TODO Read it from somewhere
root_configuration = {
    'configuration': {
        'cash': 50000,
        'loglevel': 'INFO',
        'logfile': 'quantrade.log',
        'tickers': 'random,4',
        'port': 5555,
        'exchange': 'paris',
        'db': 'test',
        'algorithm': 'StdBased',
        'frequency': 'minute',
        'manager': 'Constant',
        'start': '2011-01-10',
        'end': '2012-07-03',
        'remote': False,
        'live': False,
        'source': 'DBPriceSource',
        'env': {}
    },
    'strategie': {
        'algorithm': {
            'debug': 0,
            'long_window': 30,
            'short_window': 25,
            'stddev_window': 9,
            'vwap_window': 5,
            'refresh_period': 1,
            'base_price': 50,
            'save': 1,
            'threshold': 0
        },
        'manager': {
            'name': 'xavier',
            'load_backup': 0,
            'max_weight': 0.3,
            'connected': 0,
            'android': 0,
            'loopback': 60,
            'source': 'mysql',
            'perc_sell': 1.0,
            'buy_amount': 80,
            'sell_amount': 70
        }
    }
}
