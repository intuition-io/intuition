from twisted.internet import protocol, reactor
from twisted.python import log
import sys
import json

#NOTE A good tuto: http://krondo.com/?page_id=1327


class Test(protocol.Protocol):

    def __init__(self, factory):
        self.answers = {'state': 'OK', None: 'Unknown command'}
        self.factory = factory

    def connectionMade(self):
        self.factory.numProtocols = self.factory.numProtocols + 1
        self.transport.write('Connected to server ({} connections)'.format(self.factory.numProtocols))

    def connectionLost(self, reason):
        print('Connection aborted.')
        self.factory.numProtocols = self.factory.numProtocols - 1

    def dataReceived(self, raw_data):
        print('Received: {}'.format(raw_data.strip()))
        data = []
        try:
            data = json.loads(raw_data.strip())
            self.jsonHandler(data)
        except:
            self.transport.write(self.answers.get(raw_data.strip(), self.answers[None]))

    def jsonHandler(self, data):
        print('Json data: {}'.format(data))
        if 'command' in data:
            if data['command'] == 'bye':
                self.transport.write('Bye dude.')
                self.transport.loseConnection()
                print('User disconnected.')
        elif 'user' in data:
            print('User connection: {}'.format(data['user']))
            self.transport.write('User status: {}\r\n'.format(self.factory.getUser(data['user'])))


class EchoFactory(protocol.ServerFactory):
    def __init__(self, name='default', **kwargs):
        self.users = kwargs.get('users', [])
        self.factory_name = name

    #protocol = Echo
    def buildProtocol(self, addr):
        return Test(self)

    def startFactory(self):
        self.numProtocols = 0
        print('Running {} factory'.format(self.factory_name))

    def stopFactory(self):
        print('Stopping {} factory'.format(self.factory_name))

    def getUser(self, user):
        if user in self.users:
            return 'Identified'
        else:
            return 'Unknown'


if __name__ == '__main__':
    ''' Start the server '''
    port = 1234
    reactor.listenTCP(port, EchoFactory('Test', users=['xavier']))
    log.startLogging(sys.stdout)
    log.msg('Simple server in construction, meant to commuicate with R.')
    reactor.run()
