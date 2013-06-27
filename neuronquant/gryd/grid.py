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


from neuronquant.deathstar import trade, complete_configuration
from neuronquant.utils.signals import SignalManager
from neuronquant.utils.utils import get_local_ip

from fabric.api import execute
from fabric.colors import green, blue

import logbook
log = logbook.Logger('Grid::Main')

from IPython.parallel import Client, error

import neuronquant.network.fabfile as fab
from neuronquant.network.dashboard import Dashboard
from neuronquant.network.dashboard import LogIO

import xmlrpclib
import time
import os
import json
from datetime import datetime


class Grid(object):
    report_path = os.path.expanduser('~/.quantrade/report')
    nodes = []
    hosts = []
    #active_engines = set()
    default_glances_port = 61209
    dashboard = Dashboard()
    app_monitored = False
    deployed = 0
    glances_instances = {}
    tasks = {}

    def __init__(self):
        #NOTE Should clean previous report_path ?
        # Intercept CTRL-C
        SignalManager()

    def get_tasks(self, path=None, remote=False, zeroconfig=False):
        if zeroconfig:
            #TODO nmap network scan, results dumped into scan.xml
            #TODO Read, store all known ips, check for unix system
            raise NotImplementedError()
        else:
            from fabfile import global_config
            self.hosts = global_config['grid']['nodes']
            self.root_name = global_config['grid']['name']
            self.port = global_config['grid']['port']

        #NOTE Remote file read ?
        if path is None:
            path = '/'.join((os.environ['QTRADE'], 'config/grid.json'))
        # Config file is a json object with each process params
        if remote:
            remote_config = fab.load_remote_file(path, ip='192.168.0.12')
            components = remote_config['components']
        else:
            with open(path, 'r') as fd:
                components = json.load(fd)['components']

        return components

    def prepare_nodes(self, monitor_app=False, push_app=False, zeroconfig=False):
        components = self.get_tasks(zeroconfig=zeroconfig)

        self.logio = LogIO(self.hosts)

        # Push and merge local changes on remote repos
        if push_app:
            execute(fab.update_git_repos)

        self._wakeup_nodes(len(components), monitor_app)

        return components

    def _wakeup_nodes(self, nbr_to_deploy, monitor=False):
        self.app_monitored = monitor
        #NOTE Repartition according available power ?
        engines_per_host = int(nbr_to_deploy / len(self.hosts))

        # Run local ipcontroller, remote monitoring, and remote ipengines
        fab.deploy_grid(engines_per_host, monitor=monitor)

        # Create ipython.parallel interface
        self.nodes = Client()
        self._wait_for_engines(nbr_to_deploy)

    def _wait_for_engines(self, nbr_to_deploy):
        buffer_count = -1
        stuck_warning = 0
        while len(self.nodes.ids) < nbr_to_deploy:
            #FIXME Sometimes get stuck waiting forever all nodes to be online
            log.info(blue('%d node(s) online / %d' %
                     (len(self.nodes.ids), nbr_to_deploy)))
            time.sleep(6)
            if len(self.nodes.ids) == buffer_count:
                log.warning('No new nodes...')
                stuck_warning += 1
                if stuck_warning == 7:
                    #NOTE Running manually missing ones make it work...
                    log.error('** Could not run every engines')
            buffer_count = len(self.nodes.ids)
        log.info(green('Nodes ready.'))

    def deploy(self, components, is_backtest=False):
        remote_processes = {}

        # For each node:
        current_iteration = -1
        for node in self.nodes:
            # Use only idle engines
            status = node.queue_status()
            if (status['queue'] == 0) and (status['tasks'] == 0):
                current_iteration += 1
                remote_ip = node.apply_sync(get_local_ip)

                # Retrieve a common configuration template, modified by given dict
                #TODO What if len(components) != available_engines
                if 'ip' in components:
                    #NOTE An engine could be done since with checked for new nodes
                    assert remote_ip in components
                    config = complete_configuration(components[remote_ip].pop(), backtest=is_backtest)
                else:
                    config = complete_configuration(components[current_iteration], backtest=is_backtest)
                name = '-'.join((str(self.deployed),
                                 self.root_name,
                                 config['configuration']['exchange'],
                                 config['configuration']['algorithm'],
                                 config['configuration']['manager']))

                remote_processes[name] = self._process_on_engine(node, name, config, remote_ip)
                self.deployed += 1

        return remote_processes

    def _process_on_engine(self, node, name, config, remote_ip):
        self.port += 1
        config['strategie']['manager']['name'] = name
        config['configuration']['logfile'] = name + '.log'
        config['configuration']['port'] = self.port

        self.dashboard.add_description(remote_ip=remote_ip, portfolio=name)
        self.logio.add_description(name, remote_ip=remote_ip)

        # Run remote process
        log.info(blue('Running trade system on node %d::%s (%s)'
                      % (self.deployed, remote_ip, name)))
        return node.apply_async(trade, config)

    def set_monitoring(self,
                       dashboard=False,
                       logserver=False):
        if logserver:
            self.logio.build()
            self.logio.run()
            log.notice('Logs available at http://192.168.0.12:4000')

        if dashboard:
            self.dashboard.build()
            self.dashboard.run(public_ip=False)
            log.notice('Dasboard available at http://192.168.0.12:28778')

        log.info(blue('Done with remote deployement'))

        # Monitoring servers and remote processes
        # API: https://github.com/nicolargo/glances/wiki/The-Glances-API-How-To
        if self.app_monitored:
            for ip in self.hosts:
                if ip not in self.glances_instances:
                    self.glances_instances[ip] = xmlrpclib.ServerProxy(
                        'http://{}:{}'.format(ip, self.default_glances_port))
                    #msg = '{} cores available on remote host'
                    #FIXME Not supported: log.info(red(msg.format(monitor_server.getCore())))
        else:
            self.glances_instances = {}

        return self.glances_instances

    def on_end(self, id, process):
        try:
            log.info(process.get())
        except error.RemoteError, e:
            log.error('Process {} ended with an exception: {}'.format(id, e))
            with open('.'.join((self.report_path, self.hosts[0], 'md')), "a") as f:
                f.write('[{}] {} - {}\n'.format(datetime.now(), id, e))

    def _check_new_nodes(self):
        #NOTE Check for available workers ? or validate ?
        #ipdb> self.nodes.queue_status()
        #{0: {'queue': 0, 'completed': 0, 'tasks': 0}, 1: {'queue': 0, 'completed': 0, 'tasks': 0}, 'unassigned': 0}
        return (len(self.nodes.ids) - self.deployed)

    #NOTE Default behavior only for is_backtest and zeroconfig
    def update(self, dashboard, logserver):
        components = remote_processes = glances_instances = {}
        if self._check_new_nodes():
            log.info(blue('{} new nodes available'.format(
                self._check_new_nodes())))
            # If new engines are available, a new config is ready remotely
            components = self.get_tasks(remote=True)
            remote_processes = self.deploy(components)
            glances_instances = self.set_monitoring(dashboard, logserver)

        return components, remote_processes, glances_instances

    def __del__(self):
        log.info(blue('Shutting down grid computer'))
        for node in self.nodes:
            log.info(blue('Stopping node {}'.format(node.targets)))
            node.shutdown()
