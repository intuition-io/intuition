#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2013 xavier <xavier@laptop-300E5A>
#
# Distributed under terms of the MIT license.

from neuronquant.deathstar import trade, get_configuration
import neuronquant.utils.utils as utils
from neuronquant.utils.signals import SignalManager

from IPython.parallel import Client

from fabric.api import run, local, env, execute, parallel, roles, hide, cd
from fabric.colors import red, blue

from multiprocessing import Process
import time
import argparse
import logbook
log = logbook.Logger('Grid')

import xmlrpclib
import json

import jinja2


env.roledefs = {
    'controller': ['localhost'],
    'nodes': ['192.168.0.17']
}


@roles('controller')
def activate_controller():
    log.info(blue('Running ipcontroller on local machine'))
    with hide('output'):
        local('ipcontroller --reuse --ip={} &'.format(utils.get_ip(public=False)))
        local('scp /home/xavier/.config/ipython/profile_default/security/ipcontroller-engine.json xavier@192.168.0.17:dev/')


@roles('controller')
def generate_dashboards(completion):
    log.info(blue('Generating dashboards on local machine'))
    env = jinja2.Environment(
            loader=jinja2.FileSystemLoader('/home/xavier/dev/projects/ppQuanTrade/scripts/templates'))
    template = env.get_template('build_core.rake')
    log.info(blue('Rendering templates'))
    document = template.render(completion)
    fd = open('/home/xavier/openlibs/team_dashboard/lib/tasks/populate.rake', 'w')
    fd.write(document)
    fd.close()

    #FIXME with cd('/home/xavier/openlibs/team_dashboard'):
    local('cd ~/openlibs/team_dashboard && rake custom_populate')
    local('cd ~/openlibs/team_dashboard && rails server &')


@parallel
@roles('nodes')
def activate_node():
    log.info(blue('Running an ipengine on node %(host)s' % env))
    with hide('output'):
        run('ipengine --file=/home/xavier/dev/ipcontroller-engine.json')


@parallel
@roles('nodes')
def activate_monitoring():
    log.info(blue('Running glances in server mode on %(host)s' % env))
    run('glances -s')


@parallel
@roles('nodes')
def activate_restserver():
    log.info(blue('Waking up REST server on %(host)s' % env))
    #TODO Passwor read from default.json
    run('/home/xavier/dev/projects/ppQuanTrade/server/rest_server.js -p quantrade')


def deploy_grid(engines_per_host=1, monitor=False):
    LAUNCH_DELAY = 3
    log.info(blue('Deploying grid-tradesystem', bold=True))

    if monitor:
        #NOTE A daemon decorator ?
        #NOTE Or use dtach shell command, or pty=False
        p = Process(target=execute, args=(activate_monitoring,))
        p.start()

    execute(activate_controller)
    p = Process(target=execute, args=(activate_restserver,))
    p.start()
    for i in range(engines_per_host):
        time.sleep(LAUNCH_DELAY)
        p = Process(target=execute, args=(activate_node,))
        p.start()


def parse_command_line():
    parser = argparse.ArgumentParser(description='Grid computation system deployement script')
    parser.add_argument('-v', '--version',
                        action='version',
                        version='%(prog)s v0.8.1 Licence Apache 2.0', help='Print program version')
    parser.add_argument('-d', '--dashboard',
                        action='store_true',
                        help='To generate or not the dashboard')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_command_line()

    changes = [{'exchange': 'paris',
                'algorithm': 'StdBased',
                'manager': 'Constant',
                'tickers': 'random,20',
                'debug': 1,
                'end': '17h',
                'stddev_window': 9,
                'vwap_window': 5},
               {'manager': 'Fair'},
               {'algorithm': 'DualMA',
                'manager': 'Constant',
                'long_window': 30,
                'short_window': 20,
                'threshold': 1},
               {'algorithm': 'Momentum',
                'window_length': 5},
               {'algorithm': 'VWAP',
                'window_length': 3},
               {'algorithm': 'BuyAndHold'},
               {'algorithm': 'Follower',
                'refresh_period': 1,
                'window_length': 30},
               {'manager': 'Fair'},
               {'algorithm': 'AASL',
                'base_price': 50},
               {'manager': 'Constant'},
                # Forex
               {'exchange': 'forex',
                'algorithm': 'StdBased',
                'manager': 'Constant',
                'tickers': 'EUR/USD,EUR/GBP,EUR/JPY,GBP/USD,USD/CHF,EUR/JPY,EUR/CHF,USD/CAD,AUD/USD,GBP/JPY',
                'debug': 1,
                'end': '18h',
                'stddev_window': 9,
                'vwap_window': 5},
               {'manager': 'Fair'},
               {'algorithm': 'DualMA',
                'manager': 'Constant',
                'long_window': 30,
                'short_window': 20,
                'threshold': 1},
               {'algorithm': 'Momentum',
                'window_length': 5},
               {'algorithm': 'VWAP',
                'window_length': 3},
               {'algorithm': 'BuyAndHold'},
               {'algorithm': 'Follower',
                'refresh_period': 1,
                'window_length': 30},
               {'manager': 'Fair'},
               {'algorithm': 'AASL',
                'base_price': 50},
               {'manager': 'Constant'}
    ]

    #TODO nmap network scan, results dumped into scan.xml
    #TODO Read, store all known ips, check for unix system

    signals = SignalManager()
    root_name = 'xavier'
    root_port = 5555
    engines_per_host = len(changes)
    hosts = ['192.168.0.17']

    if len(hosts) > 0:
        #TODO Install or update neuronquant with local (latest) version

        # Run local ipcontroller, remote monitoring, and remote ipengines
        deploy_grid(engines_per_host, monitor=True)

        # Create ipython.parallel interface
        time.sleep(engines_per_host * 7)
        nodes = Client()
        log.info(blue('%d node(s) online' % len(nodes.ids)))
        assert len(nodes.ids) == len(changes)

        # For each node:
        remote_processes = []
        completion = {'panel': []}
        for i, node in enumerate(nodes):
            #name = '-'.join((root_name, 'remote', str(i)))
            config = get_configuration(changes[i], backtest=False)

            name = '-'.join((str(i), root_name, config['exchange'],
                config['algorithm'], config['manager']))
            config['manager']['name'] = name
            config['configuration']['logfile'] = name + '.log'
            config['configuration']['port'] = root_port + i
            log.info(blue('Running trade system on node %d (%s)' % (i, name)))

            description = {'i': i, 'title': name, 'proxy_ip': '192.168.0.17', 'portfolio': name}
            completion['panel'].append(description)

            # Run remote process
            remote = node.apply(trade, config)
            remote_processes.append(remote)

        if args.dashboard:
            generate_dashboards(completion)

        # Monitoring servers
        # API: https://github.com/nicolargo/glances/wiki/The-Glances-API-How-To
        monitor_server = xmlrpclib.ServerProxy('http://192.168.0.17:61209')
        log.info(red('{} cores available on remote host'.format(monitor_server.getCore())))
        while True:
            cpu_infos = json.loads(monitor_server.getCpu())
            log.info(red('System cpu use: {}'.format(cpu_infos['system'])))
            log.info(red('User cpu use: {}'.format(cpu_infos['user'])))
            log.info(red(json.loads(monitor_server.getLoad())))
            for process in remote_processes:
                log.info(blue('Process elapsed {}'.format(process.elapsed)))
                log.info(blue('Process progress {}'.format(process.progress)))
                if process.ready():
                    log.info(blue('Process ended: {}'.format(process.successful())))
                    log.info(blue(process.get()))
            time.sleep(60)
