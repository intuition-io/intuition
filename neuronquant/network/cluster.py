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
log = logbook.Logger('Grid::Main')

from neuronquant.utils.signals import SignalManager
from neuronquant.utils.utils import get_local_ip
from neuronquant.network.dashboard import Dashboard
from neuronquant.network.dashboard import LogIO
import neuronquant.network.fabfile as fab

from IPython.parallel import Client

from fabric.api import (
    env, execute
)


CONFIG_PATH = os.path.expanduser('~/.quantrade/default.json')
TASKS_PATH = os.path.expanduser('~/dev/projects/ppQuanTrade/config/grid.json')


class Drone(object):
    '''
    A drone is a remote/local engine you can run tasks on
    '''

    def __init__(self, engine, configuration):
        self.engine = engine
        self.configuration = configuration
        self.ip = engine.apply_sync(get_local_ip)

        self.status = engine.queue_status()
        assert ((self.status['queue'] == 0) and (self.status['tasks'] == 0))

        log.debug('Using new drone on {} With configuration:\n{}'.format(
            self.ip, configuration))

    def run(self, function):
        '''
        Use Ipython remote ipengine to execute the given function
        '''
        return self.engine.apply_async(function, self.configuration)


class Node(object):
    '''
    A node is a physical machine, part of the cluster It runs glances, rest
    servers, drones and is optimized for quantrade execution
    '''

    def __init__(self, ip):
        self.ip = ip
        self.drones = []
        self.tasks = []

    def register_drone(self, engine):
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
        self.drones.append(Drone(engine, self.tasks.pop()))

    def _fetch_tasks(self, remote_path):
        '''
        When new drones are ready it means you can run tasks configured where
        they come from
        '''
        new_tasks = execute(fab.load_remote_file, remote_path, host=self.ip)
        assert self.ip in new_tasks
        self.tasks.extend(new_tasks[self.ip]['components'])


class TasksManager(object):
    '''
    Handle pending and running trading tasks through Grid runtime

    Tasks are arrays of configurations, indexed by the ip to run it on. An ip
    of 0 means it doesn't care/know where to run
    '''

    tasks = {}

    def _is_idle(self, state):
        '''
        Check if there is pending tasks to do
        '''
        if 'queue' in state:
            return not state['queue']

        # Else, no informations to answer
        return None


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

    It basically waits for new tasks to pop (ie remote drones to appear), and
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

        # It will keep track of pending and running tasks
        self.tasksmanager = TasksManager()

        # Team_dashboard web graphs
        self.dashboard = Dashboard()
        # Logs monitoring
        self.logio = LogIO(self.configuration['nodes'])

        # Nodes are physical machines of the cluster
        self.nodes = {ip: Node(ip) for ip in self.configuration['nodes']}

        self.processed_drones = []

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
        Set up local ipcontroller and activate glances monitoring and
        rest_server on provided nodes
        '''
        log.info('Deploying grid trade-system')
        log.info('Activating local ipcontroller')
        execute(fab.activate_controller)

        log.info('Activating remote glances monitoring')
        execute(fab.activate_monitoring)

        log.info('Activating remote rest_servers')
        execute(fab.activate_restserver)

        # Main interface to drones
        self.drones = Client()

    def _check_new_drones(self):
        new_drones = []
        drones_status = self.drones.queue_status()
        #NOTE what is the use of status['unassigned'] ?
        for key, state in drones_status.iteritems():
            if key == 'unassigned':
                continue
            if (self.tasksmanager._is_idle(state)
                    and key not in self.processed_drones):
                self.processed_drones.append(key)
                new_drones.append(self.drones[key])

        self._dispatch_drones(new_drones)
        return len(new_drones)

    def _dispatch_drones(self, drones):
        for drone in drones:
            ip = drone.apply_sync(get_local_ip)
            log.info('New drone detected on {}'.format(ip))
            if ip not in self.nodes:
                log.info('New node connected')
                self.nodes[ip] = Node(ip)

            self.nodes[ip].register_drone(drone)
            log.info('Drone registered')


if __name__ == '__main__':
    #from neuronquant.utils.utils import activate_pdb_hook
    #activate_pdb_hook()
    grid = Grid()
    grid.deploy()
    import time
    while True:
        time.sleep(10)
        print grid._check_new_drones()
