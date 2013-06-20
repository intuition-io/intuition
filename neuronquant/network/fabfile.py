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

import shutil

from fabric.contrib.files import get, exists
from fabric.api import (
    run, local, env, execute,
    parallel, roles, hide, sudo, settings)
from fabric.colors import blue
from fabric.context_managers import shell_env

from multiprocessing import Process
import time
import os
import json
import logbook
log = logbook.Logger('Grid::Fabric')


#FIXME local('ps') based method raise an exception when false


#TODO A function to scan all of this ?
#FIXME HARD CODED
engines_path = '/home/xavier/.config/ipython/profile_default/security/ipcontroller-engine.json'
node_path = "/home/xavier/.nvm/v0.10.7/lib/node_modules"
node_config = "/home/xavier/.quantrade"
restserver_path = '/home/xavier/dev/projects/ppQuanTrade/server/rest_server.js'

global_config = json.load(open(os.path.expanduser('~/.quantrade/default.json'), 'r'))

#http://docs.fabfile.org/en/1.4.3/usage/env.html#full-list-of-env-vars
#env.forward_agent = True
#env.key_filename = [""]
env.user = global_config['grid']['name']
env.password = global_config['grid']['password']
env.hosts = global_config['grid']['nodes']
env.roledefs = {
    'local': ['127.0.0.1'],
    'controller': global_config['grid']['controller'],
    'nodes': global_config['grid']['nodes']
}


@roles('controller')
def activate_controller():
    if is_running(local, 'ipcontroller'):
        return

    log.info(blue('Running ipcontroller on local machine'))
    with hide('output'):
        #local('ipcontroller --reuse --ip={} &'.format(
        local('ipcontroller --ip={} &'.format(
            utils.get_local_ip(public=False)))
        #FIXME env.host=localhost
        time.sleep(2)
        for target_ip in env.hosts:
            if target_ip == utils.get_local_ip():
                local('cp {} /home/{}/dev/'.format(engines_path, env.user))
            else:
                local('scp {} {}@{}:dev/'.format(engines_path, env.user, target_ip))


@parallel
@roles('nodes')
def activate_node():
    log.info(blue('Running an ipengine on node %(host)s' % env))
    #NOTE In local do something with ipcluster ?
    with hide('output'):
        if env.host == utils.get_local_ip():
            local('ipengine --file=/home/{}/dev/ipcontroller-engine.json'.format(env.user))
        else:
            run('ipengine --file=/home/{}/dev/ipcontroller-engine.json'.format(env.user), pty=False)


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
        project, utils.get_local_ip(public=False), project))
    sudo('cp -r /home/xavier/dev/projects/ppQuanTrade/neuronquant/ \
            /usr/local/lib/python2.7/dist-packages/')


@parallel
@roles('nodes')
def activate_monitoring():
    log.info(blue('Running glances in server mode on %(host)s' % env))
    if env.host == utils.get_local_ip():
        if not is_running(local, 'glances'):
            local('glances -s &')
    else:
        if not is_running(run, 'glances'):
            run('glances -s &', pty=False)


@parallel
@roles('nodes')
def activate_restserver():
    #print("Executing on %(host)s as %(user)s" % env)
    #env.host_string = env.host
    log.info(blue('Waking up REST server on %(host)s' % env))
    #with hide('output'):
    with shell_env(NODE_PATH=node_path, NODE_CONFIG_DIR=node_config):
        if env.host == utils.get_local_ip():
            if not is_running(local, 'rest_server'):
                local('node {} &'.format(restserver_path))
        else:
            if not is_running(run, 'rest_server'):
                run('node {} &'.format(restserver_path), pty=False)


def is_running(execute, name, go_on=True, kill=False):
    with settings(warn_only=go_on):
        if execute.func_name == 'local':
            output = execute('ps -eaf | grep {} | grep -v grep'.format(name), capture=True)
        else:
            output = execute('ps -eaf | grep {} | grep -v grep'.format(name))
    if output.failed:
        log.debug(blue('{} is not running'.format(name)))
        pid = 0
    else:
        pid = output.split()[1]
        log.debug(blue('{} is running with pid {}'.format(name, pid)))
        if kill:
            log.debug(blue('Killing process {}'.format(name)))
            execute('kill -9 {}'.format(pid))

    # Make sure process has been killed before new treatment
    time.sleep(1)
    return pid


def load_remote_file(path):
    content = {}
    filename = path.split('/')[-1]
    log.info('Remotely loading {} file'.format(filename))
    if exists(path, verbose=True):
        log.debug('Found remote file {}, downloading it'.format(path))
        local_paths = get(path)
        assert not len(local_paths.failed)

        for path in local_paths:
            if os.path.exists(path):
                with open(path, 'r') as fd:
                    content = json.load(fd)
                shutil.rmtree(path[:path.rfind('/')])
            else:
                log.warning('! Could not find local file {}'.format(path))
                content = {}
    else:
        log.warning('! Could not find remote file {}'.format(path))

    log.debug(content)

    return content


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
