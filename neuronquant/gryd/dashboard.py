#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2013 xavier <xavier@laptop-300E5A>
#
# Distributed under terms of the MIT license.

'''
Dashboard class that interact with team_dashboard REST API
'''


import jinja2
import requests
import logbook
import json
import os
log = logbook.Logger('Dashboard')

import gryd.utils as utils
from gryd.fabfile import is_running

from fabric.api import (
    run, local, env, execute,
    hide, parallel, roles, settings)
from fabric.colors import blue
from fabric.context_managers import shell_env

from multiprocessing import Process

import time


#TODO Find a way to merge this replicate with fabfile
global_config = json.load(
    open(os.path.expanduser('~/.quantrade/default.json'), 'r'))

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


def proxy_request(root_uri='http://127.0.0.1:3000/api/dashboards',
                  path='',
                  payload=None,
                  method=requests.get,
                  headers={'content-type': 'application/json'}):
    try:
        if payload is None:
            response = method('/'.join((root_uri, str(path))),
                              headers=headers)
        else:
            response = method('/'.join((root_uri, str(path))),
                              data=json.dumps(payload),
                              headers=headers)
    except requests.ConnectionError:
        log.error('** Dashboard is probably down')
        return {}

    log.debug('Server response: {} in {}s'.format(response.status_code, response.elapsed.total_seconds()))
    if method == requests.delete:
        return {}
    if not response.ok:
        log.warning('** Server responded with {}::{}'.format(response.status_code, response.reason))
        return {}
    try:
        return response.json()
    except ValueError:
        log.error('** Could not decode json response')
        return {}
    return {}


def get_dashboard_list():
    return proxy_request()


def get_dashboard_info(dashboard_id):
    return proxy_request(path=dashboard_id,
                         method=requests.get)


def create_dashboard(name='Undefined'):
    return proxy_request(payload={'name': name},
                         method=requests.post)


def delete_dashboard(dashboard_id):
    return proxy_request(path=dashboard_id,
                         method=requests.delete)


def get_widgets_list(dashboard_id):
    return proxy_request(path='/'.join((str(dashboard_id), 'widgets')))


def get_widget_info(dashboard_id, widget_id):
    return proxy_request(path='/'.join((str(dashboard_id), 'widgets', str(widget_id))))


#TODO Implement and test all other parameters
#NOTE default is 30min, graph
def create_widget(dashboard_id, properties={'name': 'undefined', 'source': 'demo'}):
    return proxy_request(path='/'.join((str(dashboard_id), 'widgets')),
                              payload=properties,
                              method=requests.post)


def delete_widget(dashboard_id, widget_id):
    return proxy_request(path='/'.join((str(dashboard_id), 'widgets', str(widget_id))),
                         method=requests.delete)


#TODO Like for symbols, an abstraction between names and ids
#TODO Check for allowed values, like update_interval
class Dashboard(object):
    #NOTE templates_path could be an env variable as well
    templates_path = '/'.join((os.environ['QTRADE'], 'config/templates'))
    #FIXME Where to put officially zipline and team_dashboard
    dashboard_path = os.path.expanduser('~/openlibs/team_dashboard')
    completion = {'panel': []}
    properties = {}
    positions_buffer = {}

    def __init__(self, id=0):
        '''
        Id can be dasboard's name or id (whatever str or int)
        '''
        id = str(id)
        dashboards_list = get_dashboard_list()
        for dashboard in dashboards_list:
            #FIXME Find to many dashboards
            #if (id == str(dashboard['id'])) or (id.find(dashboard['name'])):
            if (id == str(dashboard['id'])) or (id == dashboard['name']):
                log.debug('Found dashboard with provided id')
                self.properties = dashboard
        if not self.properties:
            log.warning('Unabled to find provided id')

    def add_number_widget(self, widget_properties={'name': 'undefined', 'source': 'demo'}):
        '''
        {u'col': None,
         u'created_at': u'2013-05-07T21:41:32Z',
         u'dashboard_id': 9,
         u'id': 47,
         u'kind': u'number',
         u'label': u'euros',
         u'name': u'again',
         u'range': u'30-minutes',
         u'row': None,
         u'size': 1,
         u'size_x': 2,
         u'size_y': 2,
         u'source': u'demo',
         u'targets': None,
         u'update_interval': 60,
         u'updated_at': u'2013-05-07T21:41:32Z',
         u'use_metric_suffix': True}
        '''
        if not self.properties:
            log.warning('No dashboard connected')
            return {}
        widget_properties['kind'] = 'number'
        return create_widget(self.properties['id'], widget_properties)

    def del_widget(self, id):
        if not self.properties:
            log.warning('No dashboard connected')
            return {}
        widget_list = get_widgets_list(self.properties['id'])
        for widget in widget_list:
            if (id == str(widget['id'])) or (id == widget['name']):
                log.debug('Found widget with provided id')
                return delete_widget(widget['dashboard_id'], widget['id'])
        log.warning('Unabled to find widget with provided id')
        return {'messag': 'ressource not found'}

    def update_position_widgets(self, current_positions):
        for stock in current_positions:
            amount = current_positions[stock].amount
            stock = stock.replace(' ', '+')
            if (amount == 0) and (stock in self.positions_buffer):
                self.positions_buffer.pop(stock)
                self.del_widget(stock)
            if (amount != 0) and (stock not in self.positions_buffer):
                self.positions_buffer[stock] = amount
                self.add_number_widget(
                    {'name': stock,
                     'source': 'http_proxy',
                     'proxy_url': 'http://127.0.0.1:8080/dashboard/number?data=Amount&table=Positions&field=Ticker&value={}'.format(stock),
                     'proxy_value_path': ' ',
                     'label': '$',
                     'update_interval': '30',
                     'use_metrics_suffix': True})

    def _build_proxy_url(self):
        '''
        url proxy api abstraction
        '''
        pass

    def build(self):
        #NOTE Check quantlab for a generic version
        tpl_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.templates_path))
        template = tpl_env.get_template('dashboard_block.tpl')
        log.info('Rendering templates')
        document = template.render(self.completion)
        fd = open('{}/lib/tasks/populate.rake'.format(self.dashboard_path), 'w')
        fd.write(document)
        fd.close()

    @roles('controller')
    def run(self, port=4000, public_ip=False):
        # Make sure no dashboard is already running
        self.shutdown()

        #NOTE run() in 'controller' role = local() ?
        #TODO with fabric.cd()
        with hide('output'):
            log.info(blue('Cleaning up previous layout'))
            local('cd {} && rake cleanup'.format(self.dashboard_path))
            log.info(blue('Populating database'))
            local('cd {} && rake custom_populate'.format(self.dashboard_path))
            log.info(blue('Running server'))
            local('cd {} && rails server -p {} -b {} &'.format(
                self.dashboard_path, port, utils.get_local_ip(public=public_ip)))

    @roles('controller')
    def shutdown(self):
        pid_path = '/'.join((self.dashboard_path, 'tmp/pids/server.pid'))
        with settings(warn_only=True):
            if local('ps -e | grep $(cat {})'.format(pid_path), capture=True):
                log.info(blue('Killing deprecated process'))
                local('kill -9 $(cat {})'.format(pid_path))
            else:
                log.info('No running dashboard found')

    def add_description(self, title=None, remote_ip='127.0.0.1', portfolio='ChuckNorris'):
        if title is None:
            title = portfolio
        self.completion['panel'].append(
            {
                'i': len(self.completion['panel']) + 1,
                'title': title,
                'proxy_ip': remote_ip,
                'portfolio': portfolio
            }
        )
        return self.completion

    def __del__(self):
        self.shutdown()


#NOTE Factorize Dashboard and LogIO ?
class LogIO(object):
    templates_path = '/'.join((os.environ['QTRADE'], 'config/templates'))
    #FIXME xavier == $USER
    node_path = "/home/xavier/.nvm/v0.10.7/lib/node_modules"

    def __init__(self, hosts):
        self.completion = {ip: {'logfiles': []} for ip in hosts}

    def build(self):
        #TODO integrate server ip in the template
        #TODO Clean previous log files
        for remote_ip, completion in self.completion.iteritems():
            log.info(blue('Running log watcher on remote machine'))
            tpl_env = jinja2.Environment(
                loader=jinja2.FileSystemLoader(self.templates_path))
            template = tpl_env.get_template('logs_block.tpl')
            log.info(blue('Rendering templates'))
            document = template.render(completion)
            fd = open('{}/{}-harvester.conf'.format(self.templates_path, remote_ip), 'w')
            fd.write(document)
            fd.close()

    def run(self):
        p = Process(target=execute, args=(self._run_server,))
        p.start()
        time.sleep(2)
        p = Process(target=execute, args=(self._run_harvester,))
        p.start()

    @parallel
    @roles('controller')
    def _run_server(self):
        #try:
            #pid = local('ps -C node | grep log.io-server | cut -d" " -f6', capture=True)
        #except:
        if not is_running(local, 'log.io-server'):
            with shell_env(NODE_PATH=self.node_path):
                local('log.io-server')

    @parallel
    @roles('nodes')
    def _run_harvester(self):
        #time.sleep(10)
        #NOTE I could run it on local as well to inspect report files
        #run('rm /home/xavier/.quantrade/log/*')
        if env.host == utils.get_local_ip():
            local('cp {}/{}-harvester.conf /home/{}/.log.io/harvester.conf'.format(
                self.templates_path, env.host, env.user))
            is_running(local, 'log.io-harvester', kill=True)
            with shell_env(NODE_PATH=self.node_path):
                with hide('output'):
                    local('log.io-harvester')
        else:
            local('scp {}/{}-harvester.conf {}@{}:.log.io/harvester.conf'.format(
                self.templates_path, env.host, env.user, env.host))
            is_running(run, 'log.io-harvester', kill=True)
            with shell_env(NODE_PATH=self.node_path):
                with hide('output'):
                    run('log.io-harvester')

    def add_description(self, name, remote_ip='127.0.0.1'):
        # Trick to handle json structure (last coma of the line)
        if 'nodename' not in self.completion[remote_ip]:
            self.completion[remote_ip]['last'] = name + '.log'
            self.completion[remote_ip]['nodename'] = remote_ip
            self.completion[remote_ip]['server_ip'] = utils.get_local_ip()

        else:
            self.completion[remote_ip]['logfiles'].append({'name': name + '.log'})

        return self.completion
