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


import requests
import logbook
import json
log = logbook.Logger('Dashboard')


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
    properties = {}
    positions_buffer = {}

    def __init__(self, id):
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

    def update_position_widgets(current_positions):
        for stock in current_positions:
            amount = current_positions[stock].amount
            stock = stock.replace(' ', '+')
            if (amount == 0) and (stock in self.positions_buffer):
                self.positions_buffer.pop(stock)
                dashboard.del_widget(stock)
            if (amount != 0) and (stock not in self.positions_buffer):
                self.positions_buffer[stock] = amount
                dashboard.add_number_widget(
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
