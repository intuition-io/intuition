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


import neuronquant.utils.utils as utils

from fabric.api import (
    run, local, env, execute,
    parallel, roles, hide, sudo)
from fabric.colors import blue

from multiprocessing import Process
import time
import os
import json
import logbook
log = logbook.Logger('Grid::Fabric')

import jinja2


templates_path = '/home/xavier/dev/projects/ppQuanTrade/scripts/templates'
dashboard_path = '/home/xavier/openlibs/team_dashboard'
engines_path = '/home/xavier/.config/ipython/profile_default/security/ipcontroller-engine.json'

global_config = json.load(open(os.path.expanduser('~/.quantrade/default.json'), 'r'))

env.roledefs = {
    'controller': global_config['grid']['controller'],
    'nodes': global_config['grid']['nodes']
}


@roles('controller')
def activate_controller():
    log.info(blue('Running ipcontroller on local machine'))
    with hide('output'):
        #local('ipcontroller --reuse --ip={} &'.format(
        local('ipcontroller --ip={} &'.format(
            utils.get_ip(public=False)))
        #FIXME env.host=localhost
        time.sleep(2)
        local('scp {} {}@{}:dev/'.format(engines_path, env.user, '192.168.0.17'))


@roles('controller')
def generate_dashboards(completion):
    log.info(blue('Generating dashboards on local machine'))
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(templates_path))
    template = env.get_template('build_core.rake')
    log.info(blue('Rendering templates'))
    document = template.render(completion)
    fd = open('{}/lib/tasks/populate.rake'.format(dashboard_path), 'w')
    fd.write(document)
    fd.close()

    #FIXME with cd('/home/xavier/openlibs/team_dashboard'):
    with hide('output'):
        local('cd {} && rake cleanup'.format(dashboard_path))
        local('cd {} && rake custom_populate'.format(dashboard_path))
        local('cd {} && rails server -p 4000 -b {} &'.format(
            dashboard_path, utils.get_ip()))


#FIXME Should be installed on controller and only ran here
@parallel
@roles('nodes')
def run_logserver():
    run('rm /home/xavier/.quantrade/log/*')
    run('log.io-server')


@parallel
@roles('nodes')
def run_logharvester():
    run('log.io-harvester')


def activate_logserver(completion):
    #TODO integrate ip in the template
    #TODO Clean previous log files
    log.info(blue('Running log watcher on remote machine'))
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(templates_path))
    template = env.get_template('template.logs')
    log.info(blue('Rendering templates'))
    document = template.render(completion)
    fd = open('{}/harvester.conf'.format(templates_path), 'w')
    fd.write(document)
    fd.close()

    #with hide('output'):
    local('scp {}/harvester.conf {}@{}:.log.io/'.format(
        templates_path, 'xavier', '192.168.0.17'))
        #FIXME templates_path, env.user, env.host))
    p = Process(target=execute, args=(run_logserver,))
    p.start()
    time.sleep(2)
    p = Process(target=execute, args=(run_logharvester,))
    p.start()


@parallel
@roles('nodes')
def activate_node():
    log.info(blue('Running an ipengine on node %(host)s' % env))
    with hide('output'):
        run('ipengine --file=/home/xavier/dev/ipcontroller-engine.json')


#FIXME sudo in parallel
@roles('nodes')
def update_git_repos():
    project = 'ppQuanTrade'
    #TODO use setup.py instead
    #TODO More generic command
    log.info(blue('Updating remote version of ppQuanTrade %(host)s' % env))
    #TODO Use get_ip()
    run('cd /home/xavier/dev/projects/{} && \
            git pull xavier@{}:dev/projects/{}'.format(
        project, utils.get_ip(public=False), project))
    sudo('cp -r /home/xavier/dev/projects/ppQuanTrade/neuronquant/ \
            /usr/local/lib/python2.7/dist-packages/')


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
    with hide('output'):
        run('/home/xavier/dev/projects/ppQuanTrade/server/rest_server.js')


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
