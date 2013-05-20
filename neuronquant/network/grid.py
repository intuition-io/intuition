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


from neuronquant.deathstar import trade, get_configuration
from neuronquant.utils.signals import SignalManager

from fabric.api import execute
from fabric.colors import red, blue

import logbook
log = logbook.Logger('Grid::Main')

from IPython.parallel import Client

import neuronquant.network.fabfile as fab

import xmlrpclib
import time
import os
import json


class Grid(object):
    def __init__(self):
        # Intercept CTRL-C
        SignalManager()

    def setup(self, monitor_app=False, push_app=False, zeroconfig=False):
        # config file is a json object with each process params
        fd = open('/'.join((os.environ['QTRADE'], 'config/grid.json')), 'r')
        components = json.load(fd)['components']

        if zeroconfig:
            #TODO nmap network scan, results dumped into scan.xml
            #TODO Read, store all known ips, check for unix system,
            #     quant installed
            raise NotImplementedError
        else:
            from fabfile import global_config
            hosts = global_config['grid']['nodes']
            self.root_name = global_config['grid']['name']
            self.root_port = global_config['grid']['port']

        #NOTE Repartition according power ?
        engines_per_host = int(len(components) / len(hosts))

        # Push and merge local changes on remote repos
        if push_app:
            execute(fab.update_git_repos)

        # Run local ipcontroller, remote monitoring, and remote ipengines
        fab.deploy_grid(engines_per_host, monitor=monitor_app)

        #TODO Better Wait for controller and engines to be started
        # Create ipython.parallel interface
        self.nodes = Client()
        log.info(blue('%d components to run' % len(components)))
        while len(self.nodes.ids) < len(components):
            log.info(blue('%d node(s) online' % len(self.nodes.ids)))
            time.sleep(4)
        log.info(blue('%d node(s) online' % len(self.nodes.ids)))

        return components

    def deploy(self, components, is_backtest=False):
        # Useful dicts, see below
        remote_processes = {}
        completion_dashboard = {'panel': []}
        completion_logs = {'logfiles': []}

        # For each node:
        for i, node in enumerate(self.nodes):
            # Retrieve a common configuration template, modified by given dict
            config = get_configuration(components[i], backtest=is_backtest)

            name = '-'.join((str(i),
                             self.root_name,
                             config['configuration']['exchange'],
                             config['configuration']['algorithm'],
                             config['configuration']['manager']))
            config['strategie']['manager']['name'] = name
            config['configuration']['logfile'] = name + '.log'
            config['configuration']['port'] = self.root_port + i

            log.info(blue('Running trade system on node %d (%s)' % (i, name)))

            #NOTE do node object have the IP adress ?
            #     Seems not but access to node.targets, map them to ip ?
            completion_dashboard['panel'].append(
                {
                    'i': i, 'title': name,
                    'proxy_ip': '192.168.0.17',
                    'portfolio': name
                }
            )

            # Trick to handle json strucutre (last coma of the line)
            if i == len(self.nodes) - 1:
                completion_logs['last'] = name + '.log'
            else:
                completion_logs['logfiles'].append({'name': name + '.log'})

            # Run remote process
            remote_processes[name] = node.apply(trade, config)

        return remote_processes, completion_logs, completion_dashboard

    def setup_monitoring(self, glances_server=False,
                         completion_dashboard=False,
                         completion_logserver=False):
        if completion_logserver:
            fab.activate_logserver(completion_logserver)

        if completion_dashboard:
            fab.generate_dashboards(completion_dashboard)

        log.info(blue('Done with remote deployement'))

        #TODO Improve, and take care of provided flags
        # Monitoring servers and remote processes
        # API: https://github.com/nicolargo/glances/wiki/The-Glances-API-How-To
        if glances_server:
            monitor_server = xmlrpclib.ServerProxy('http://192.168.0.17:61209')
            msg = '{} cores available on remote host'
            log.info(red(msg.format(monitor_server.getCore())))
        else:
            monitor_server = None

        return monitor_server

    def __del__(self):
        log.info(blue('Shutting down grid computer'))
        for node in self.nodes:
            log.info(blue('Stopping node {}'.format(node.targets)))
            node.shutdown()
