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


#TODO A function to scan all of this ?
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


@parallel
@roles('nodes')
def activate_node():
    log.info(blue('Running an ipengine on node %(host)s' % env))
    #NOTE In local do something with ipcluster ?
    with hide('output'):
        if env.host == utils.get_ip():
            local('ipengine --file=/home/{}/dev/ipcontroller-engine.json'.format(env.user))
        else:
            run('ipengine --file=/home/{}/dev/ipcontroller-engine.json'.format(env.user))


#FIXME sudo in parallel
#NOTE Will be replaced by mina, or other much more robust deploy stuff
@roles('nodes')
def update_git_repos():
    project = 'ppQuanTrade'
    #TODO use setup.py instead
    #TODO More generic command
    log.info(blue('Updating remote version of ppQuanTrade %(host)s' % env))
    run('cd /home/xavier/dev/projects/{} && \
            git pull xavier@{}:dev/projects/{}'.format(
        project, utils.get_ip(public=False), project))
    sudo('cp -r /home/xavier/dev/projects/ppQuanTrade/neuronquant/ \
            /usr/local/lib/python2.7/dist-packages/')


@parallel
@roles('nodes')
def activate_monitoring():
    log.info(blue('Running glances in server mode on %(host)s' % env))
    if env.host == utils.get_ip():
        local('glances -s')
    else:
        run('glances -s')


@parallel
@roles('nodes')
def activate_restserver():
    log.info(blue('Waking up REST server on %(host)s' % env))
    #with hide('output'):
    with shell_env(NODE_PATH=node_path, NODE_CONFIG_DIR='/home/xavier/.quantrade/'):
        print env.host
        if env.host == utils.get_ip():
            local('node /home/xavier/dev/projects/ppQuanTrade/server/rest_server.js')
        else:
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
