#! /usr/bin/env python
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


from fabric.colors import red, blue, cyan

import os
import time
import argparse
import logbook
log = logbook.Logger('Grid::Main')

import json

from neuronquant.network.grid import Grid


def parse_command_line():
    parser = argparse.ArgumentParser(
        description='Grid computation system deployement script')
    parser.add_argument('-v', '--version',
                        action='version',
                        version='%(prog)s v0.8.1 Licence Apache 2.0',
                        help='Print program version')
    parser.add_argument('-a', '--heartbeat',
                        type=int, action='store', default=30,
                        required=False,
                        help='Interval to ask news to the nodes')
    parser.add_argument('-d', '--dashboard',
                        action='store_true',
                        help='To generate or not the dashboard')
    parser.add_argument('-m', '--monitor',
                        action='store_true',
                        help='Run a remote glances instance and check it')
    parser.add_argument('-z', '--zeroconfig',
                        action='store_true',
                        help='Detect remote hosts on LAN')
    parser.add_argument('-p', '--pushapp',
                        action='store_true',
                        help='Push local app version on server')
    parser.add_argument('-l', '--logserver',
                        action='store_true',
                        help='Run log.io server')
    return parser.parse_args()


if __name__ == '__main__':
    os.system('clear')
    args = parse_command_line()

    grid = Grid()

    components = grid.prepare_nodes(args.monitor, args.pushapp, args.zeroconfig)

    remote_processes = grid.deploy(components, is_backtest=True)

    glances_instances = grid.set_monitoring(
        args.monitor,
        args.dashboard,
        args.logserver)

    if args.logserver:
        log.notice('Dasboard available at http://192.168.0.12:28778')
    if args.dashboard:
        log.notice('Logs available at http://192.168.0.12:4000')

    processes_done = set()
    living_processes = set(remote_processes.keys())
    while len(living_processes):
        #TODO Check for new nodes (ie a new engine is ready)
        #     if so, execute trade on it with configuration
        #     and update everything else
        print cyan('-' * 60)
        msg = 'Alive rate: {} / {}'
        log.info(red(msg.format(len(living_processes),
                                len(remote_processes))))
        if args.monitor:
            for ip, monitor in glances_instances.iteritems():
                log.info('Inforamtions on {}'.format(ip))
                cpu_infos = json.loads(monitor.getCpu())
                #FIXME Not supported on thib laptop
                #log.info(red('System cpu use: {}'.format(cpu_infos['system'])))
                #log.info(red('User cpu use: {}'.format(cpu_infos['user'])))
                log.info(red(json.loads(monitor.getLoad())))

        for id, process in remote_processes.iteritems():
            log.info(blue('[{}] Uptime   {}'.format(id, process.elapsed)))
            log.info(blue('[{}] Progress {}'.format(id, process.progress)))
            if process.ready():
                msg = '[{}] Done with status: {}'
                log.info(red(msg.format(id, process.successful())))
                if id in living_processes:
                    processes_done.add(id)
                    living_processes.remove(id)
                    grid.on_end(id, process)
            print cyan('--')

        time.sleep(args.heartbeat)
    #TODO Join and terminate Ran process
    log.notice(red('All processes finished'))
