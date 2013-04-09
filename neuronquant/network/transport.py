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
import abc

from neuronquant.utils.signals import SignalManager
from neuronquant.utils import remote_setup

log = logbook.Logger('ZMQ Messaging')
#TODO http://pythonhosted.org/Logbook/setups.html
#     http://pythonhosted.org/Logbook/api/queues.html


# Alias for acknowledgment messages
OK_CODE = 0
KO_CODE = 1


class ZMQ_Base(object):
    '''
    Abstract class in common for every type of ZMQ device. Messages sent through
    network between QuanTrade processes are json, and should look like:
        {
            'time': '14, March 2012 15:12',
            'id': 'sender id',
            'channel': 'receiver id',
            'type': 'used by broker for filtering',
            'msg': 'json or plain text informations'
         }
    Most of the time messages will ben sent to the broker which will read
    those fields and route accordingly the message toward a client that
    will process the informations.
    '''

    __metaclass__ = abc.ABCMeta

    def __init__(self, id=None, recipient='dashboard', signal_manager=True):
        # Used in messages 'id' field, for authentification on receiver side
        self.identity = id

        # So said receiver, allows the broker to route the message toward the right client
        self.recipient = recipient

        # Handles especially CTRL-C keyboard interruption or alarms (when waiting with a timeout)
        signals = [signal.SIGINT]
        self.signal_manager = SignalManager(signal_codes=signals)
        log.info(self.signal_manager)

        # Every ZMQ sockets need to initialize a context
        self.context = zmq.Context()

        self.port    = None
        self.socket  = None

    def receive(self, json=True, acknowledgment=None):
        msg = None
        msg = self.socket.recv_json() if json else self.socket.recv()
        log.debug('ZMQ Agent received {}'.format(msg))

        # If requested, we let the sender know the message was received
        if acknowledgment:
            if json:
                # Complete protocole, default
                self.socket.send_json({'time': dt.datetime.strftime(dt.datetime.now(), format='%Y-%m-%dT%H:%M:%S'),
                                       'id': self.identity, 'channel': self.recipient, 'msg': OK_CODE})
            else:
                # Simple string response
                self.socket.send('{}:{}'.format(self.identity, OK_CODE))
        return msg

    def __del__(self):
        #FIXME Correct seesion end
        #if not self.socket.closed:
        #self.socket.close()
        #self.context.term()
        pass


class ZMQ_Dealer(ZMQ_Base):
    '''
    ZMQ Dealer device, http://www.zeromq.org/tutorials:dealer-and-router
    This is the client device, used by the simulator and the portfolio manager,
    and meant (but not limited) to talk to the broker.
    '''
    #NOTE Default should be reade from ~/.quantrade/default.json (method from abstract class)
    def run(self, uri=None, host='localhost', port=5570):
        '''
        Device setup and makes it listen
        '''
        # Create 'Dealer' type socket
        self.socket = self.context.socket(zmq.DEALER)
        self.port   = port

        # Set identity that will be communicated as authentification in messages
        self.socket.setsockopt(zmq.IDENTITY, self.identity if self.identity else str(self.port))

        # If no explicit uri, we use given or default host and port
        if uri is None:
            uri = 'tcp://{}:{}'.format(host, port)

        # Setup done, running
        self.socket.connect(uri)
        # Non-blocking mechanism
        self.poll = zmq.Poller()
        self.poll.register(self.socket, zmq.POLLIN)
        log.info('Client connected to {}.'.format(uri))

    def noblock_recv(self, timeout=0, json=True, acknowledgment=None):
        '''
        Checks for pending messages on socket but won't wait for new to arrive
        '''
        # Checks
        socks = dict(self.poll.poll(timeout))
        msg   = None
        # Something arrived for this device ?
        if self.socket in socks:
            # A new message is pending ?
            if socks[self.socket] == zmq.POLLIN:
                msg = self.socket.recv_json() if json else self.socket.recv()
                log.debug('Client received {}'.format(msg))

                if acknowledgment:
                    if json and msg:
                        self.send(OK_CODE, type='acknowledgment')
                    elif json and not msg:
                        self.send(KO_CODE, type='acknowledgment')
                    else:
                        self.socket.send('{}:{}'.format(self.identity, acknowledgment))
        return msg

    def send_to_android(self, msg):
        '''
        Send regular message to broker but setting channel to 'android', that
        will make it use NotifyMyAndroid to route message toward a green robot device
        '''
        assert isinstance(msg, dict)
        msg['time']    = dt.datetime.strftime(dt.datetime.now(), format = '%Y-%m-%dT%H:%M:%S')
        msg['type']    = 'notification'
        msg['channel'] = 'android'
        msg['appname'] = 'NeuronQuant'
        log.debug('Dealer sends android notification: {}'.format(msg))
        self.send(msg, format=False)

    def send(self, msg, format=True, **kwargs):
        '''
        Sends msg through socket, taking care of missing fields in protocole
        if format flag is set. Otherwise, autodetection
        '''
        if format:
            self.socket.send_json({'time': dt.datetime.strftime(dt.datetime.now(), format='%Y-%m-%dT%H:%M:%S'),
                                   'msg': msg,
                                   'id': self.identity,
                                   'channel': kwargs.get('channel', self.recipient),
                                   'type': kwargs.get('type', '')})
        else:
            self.socket.send_json(msg) if isinstance(msg, dict) else self.socket.send(msg)


#TODO Unused, cleanup
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
                    self.send({"{}:statut".format(port): OK_CODE})
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


#TODO Externalize tests
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
