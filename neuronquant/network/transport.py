#
# Copyright 2012 Xavier Bruhiere
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


import threading
import signal
import logbook

import zmq
import time
import json
import datetime as dt

from neuronquant.utils.signals import SignalManager
from neuronquant.utils import remote_setup, color_setup, setup

log = logbook.Logger('ZMQ Messaging')
#https://github.com/JustinTulloss/zeromq.node/blob/master/examples/devices/queue.js
#https://github.com/zeromq/pyzmq/blob/master/examples/device/server.py
#TODO http://pythonhosted.org/Logbook/setups.html
#     http://pythonhosted.org/Logbook/api/queues.html
#TODO 'dashboard' destination hardcoded


#TODO This class is abstract
class ZMQ_Base(object):
    '''
    Abstract class common for every type of ZMQ device
    '''
    def __init__(self, id=None, signal_manager=True):
        self.identity = id
        signals = [signal.SIGINT]
        self.signal_manager = SignalManager(signal_codes=signals)
        log.info(self.signal_manager)
        self.context = zmq.Context()
        self.port = None
        self.socket = None

    def receive(self, json=True, acknowledgment=None):
        msg = None
        msg = self.socket.recv_json() if json else self.socket.recv()
        #msg = self.socket.recv()
        log.debug('ZMQ Agent received {}'.format(msg))
        if acknowledgment:
            if json:
                self.socket.send_json({'time': dt.datetime.strftime(dt.datetime.now(), format='%Y-%m-%dT%H:%M:%S'),
                                       'id': self.identity, 'channel': 'dashboard', 'msg': 0})
            else:
                self.socket.send('{}:{}'.format(self.identity, 0))
        return msg

    def __del__(self):
        #if not self.socket.closed:
        #self.socket.close()
        #self.context.term()
        pass


class ZMQ_Dealer(ZMQ_Base):
    def run(self, uri=None, host='localhost', port=5555):
        self.socket = self.context.socket(zmq.DEALER)
        self.port = port
        self.socket.setsockopt(zmq.IDENTITY, self.identity if self.identity else str(self.port))
        if uri is None:
            uri = 'tcp://{}:{}'.format(host, port)
        self.socket.connect(uri)
        self.poll = zmq.Poller()
        self.poll.register(self.socket, zmq.POLLIN)
        log.info('Client connected to {}.'.format(uri))

    def noblock_recv(self, timeout=0, json=True, acknowledgment=None):
        socks = dict(self.poll.poll(timeout))
        msg = None
        if self.socket in socks:
            if socks[self.socket] == zmq.POLLIN:
                msg = self.socket.recv_json() if json else self.socket.recv()
                log.debug('Client received {}'.format(msg))
                if acknowledgment:
                    if json and msg:
                        self.send('ok', type='acknowledgment')
                    elif json and not msg:
                        self.send('ko', type='acknowledgment')
                    else:
                        self.socket.send('{}:{}'.format(self.identity, acknowledgment))
        return msg

    def send_to_android(self, msg):
        assert isinstance(msg, dict)
        msg['time']    = dt.datetime.strftime(dt.datetime.now(), format = '%Y-%m-%dT%H:%M:%S')
        msg['type']    = 'notification'
        msg['channel'] = 'android'
        msg['appname'] = 'NeuronQuant'
        log.debug('Client sends android notification: {}'.format(msg))
        self.send(msg, format=False)

    def send(self, msg, format=True, **kwargs):
        #log.debug('Client sends: %s' % msg)
        if format:
            self.socket.send_json({'time': dt.datetime.strftime(dt.datetime.now(), format='%Y-%m-%dT%H:%M:%S'), 'msg': msg,
                                   'id': self.identity, 'channel': kwargs.get('channel', 'dashboard'), 'type': kwargs.get('type', '')})
        else:
            self.socket.send_json(msg) if isinstance(msg, dict) else self.socket.send(msg)


class ZMQ_Broker(threading.Thread):
    """ServerTask"""
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        context = zmq.Context()
        frontend = context.socket(zmq.ROUTER)
        frontend.bind('tcp://*:5555')

        backend = context.socket(zmq.DEALER)
        backend.bind('tcp://127.0.0.1:5570')

        zmq.device(zmq.QUEUE, frontend, backend)

        frontend.close()
        backend.close()
        context.term()


class ZMQ_Server(ZMQ_Base):
    def run(self, port=5555, on_recv=None, forever=False):
        self.socket = self.context.socket(zmq.REP)
        self.port = port
        if not on_recv:
            on_recv = self.default_on_recv
        log.info('Server listening on port {}...'.format(port))
        self.socket.bind("tcp://*:%s" % port)
        msg = dict()
        if forever:
            while 'done' not in msg:
                msg = self.receive()
                try:
                    on_recv(msg, id=port)
                    self.send({"{}:statut".format(port): 0})
                except:
                    log.error('** Processing message received')
                    self.send({"{}:statut".format(port): 1})
            log.info('Termination request, stop listening...')

    def run_forever(self, port=5555, on_recv=None):
        self.run(port, on_recv, True)

    def default_on_recv(self, msg, id=1):
        log.info("Received request: {}".format(msg))
        time.sleep(1)


class ZMQ_Client(ZMQ_Base):

    def connect(self, host='localhost', ports=[5555]):
        self.socket = self.context.socket(zmq.REQ)
        self.ports = ports
        for port in ports:
            log.info('Client connecting to {} on port {}...'.format(host, port))
            self.socket.connect('tcp://{}:{}'.format(host, port))


def handle_json(msg, id):
    #print(json.dumps(json.loads(msg), indent=4, separators=(',', ': ')))
    print(json.dumps(msg, indent=4, separators=(',', ': ')))


def server_test():
    server = ZMQ_Server()
    server.run_forever(ports=5555, on_recv=handle_json)


def client_test():
    client = ZMQ_Client(timeout=5)
    client.connect(host='localhost', ports=[5555, 5555, 5555])
    for request in range(1, 5):
        reply = client.send('Hello', acknowledgment=True)
        assert(reply)


def dealer_test():
    client = ZMQ_Dealer(id='client_test')
    client.run(host='127.0.0.1', port=5570)
    client.receive()
    for request in range(2):
        client.noblock_recv()
        time.sleep(0.5)
        client.send('test number {}'.format(request), channel='dashboard', json=True)
    client.send_to_android({'title': 'Buy signal on google', 'priority': 4,
                 'description': 'Google dual moving average crossed: you should buy 23 stocks with a risk of 0.23'})

if __name__ == '__main__':
    with remote_setup.applicationbound():
        dealer_test()
