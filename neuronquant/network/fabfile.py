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
from fabric.context_managers import shell_env

from multiprocessing import Process
import time
import os
import json
import logbook
log = logbook.Logger('Grid::Fabric')

import jinja2


#TODO A function to scan all of this ?
templates_path = '/home/xavier/dev/projects/ppQuanTrade/config/templates'
dashboard_path = '/home/xavier/openlibs/team_dashboard'
engines_path = '/home/xavier/.config/ipython/profile_default/security/ipcontroller-engine.json'
node_path = "/home/xavier/.nvm/v0.10.7/lib/node_modules"

global_config = json.load(open(os.path.expanduser('~/.quantrade/default.json'), 'r'))

#http://docs.fabfile.org/en/1.4.3/usage/env.html#full-list-of-env-vars
#env.forward_agent = True
#env.key_filename = [""]
env.user = global_config['grid']['name']
env.password = global_config['grid']['password']
env.hosts = global_config['grid']['nodes']
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
        for target_ip in env.hosts:
            local('scp {} {}@{}:dev/'.format(engines_path, env.user, target_ip))


@roles('controller')
def generate_dashboards(completion):
    log.info(blue('Generating dashboards on local machine'))
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(templates_path))
    template = env.get_template('dashboard_block.tpl')
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
@roles('controller')
def run_logserver():
    #run('rm /home/xavier/.quantrade/log/report*')
    local('log.io-server')


@parallel
@roles('nodes')
def run_logharvester():
    #time.sleep(10)
    #NOTE I could run it on local as well to inspect report files
    #run('rm /home/xavier/.quantrade/log/*')
    local('scp {}/{}-harvester.conf {}@{}:.log.io/harvester.conf'.format(
        templates_path, env.host, env.user, env.host))
    #with hide('output'):
    with shell_env(NODE_PATH=node_path):
        run('log.io-harvester')


def activate_logserver(completions_dict):
    #TODO integrate server ip in the template
    #TODO Clean previous log files
    for remote_ip, completion in completions_dict.iteritems():
        log.info(blue('Running log watcher on remote machine'))
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(templates_path))
        template = env.get_template('logs_block.tpl')
        log.info(blue('Rendering templates'))
        document = template.render(completion)
        fd = open('{}/{}-harvester.conf'.format(templates_path, remote_ip), 'w')
        fd.write(document)
        fd.close()

    #with hide('output'):
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
    #with hide('output'):
    with shell_env(NODE_PATH=node_path, NODE_CONFIG_DIR='/home/xavier/.quantrade/'):
        run('node /home/xavier/dev/projects/ppQuanTrade/server/rest_server.js')


def deploy_grid(engines_per_host=1, monitor=False):
    log.info(blue('Deploying grid-tradesystem', bold=True))

    if monitor:
        #NOTE A daemon decorator ?
        #NOTE Or use dtach shell command
        p = Process(target=execute, args=(activate_monitoring,))
        p.start()

    execute(activate_controller)

    p = Process(target=execute, args=(activate_restserver,))
    p.start()

    for i in range(engines_per_host):
        # Many parallel engines at the same time make it crash
        time.sleep(1)
        p = Process(target=execute, args=(activate_node,))
        p.start()
