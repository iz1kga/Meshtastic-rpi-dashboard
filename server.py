import sys
import os

from twisted.internet import reactor
from twisted.python import log
from twisted.web.server import Site
from twisted.web.static import File

from autobahn.twisted.websocket import WebSocketServerFactory, \
    WebSocketServerProtocol, \
    listenWS

from daemons.prefab import run


class BroadcastServerProtocol(WebSocketServerProtocol):

    def onOpen(self):
        self.factory.register(self)

    def onMessage(self, payload, isBinary):
        if not isBinary:
            self.factory.broadcast(payload.decode('utf8'))

    def connectionLost(self, reason):
        WebSocketServerProtocol.connectionLost(self, reason)
        self.factory.unregister(self)


class BroadcastServerFactory(WebSocketServerFactory):

    """
    Simple broadcast server broadcasting any message it receives to all
    currently connected clients.
    """

    def __init__(self, url):
        WebSocketServerFactory.__init__(self, url)
        self.clients = []
        #self.tickcount = 0
        #self.tick()

    def tick(self):
        self.tickcount += 1
        #self.broadcast("tick %d from server" % self.tickcount)
        #reactor.callLater(1, self.tick)

    def register(self, client):
        if client not in self.clients:
            print("registered client {}".format(client.peer))
            self.broadcast('{"cmd":"update"}')
            self.clients.append(client)

    def unregister(self, client):
        if client in self.clients:
            print("unregistered client {}".format(client.peer))
            self.clients.remove(client)

    def broadcast(self, msg):
        print("broadcasting message '{}' ..".format(msg))
        for c in self.clients:
            c.sendMessage(msg.encode('utf8'))
            print("message sent to {}".format(c.peer))


class BroadcastPreparedServerFactory(BroadcastServerFactory):

    """
    Functionally same as above, but optimized broadcast using
    prepareMessage and sendPreparedMessage.
    """

    def broadcast(self, msg):
        print("broadcasting prepared message '{}' ..".format(msg))
        preparedMsg = self.prepareMessage(msg)
        for c in self.clients:
            c.sendPreparedMessage(preparedMsg)
            print("prepared message sent to {}".format(c.peer))


class serverDaemon(run.RunDaemon):
    def run(self):
        runWebSocket("ws://0.0.0.0:9000", 9001)

def runWebSocket(ws,httpPort):
    workDir = os.path.dirname(__file__)+"/webClient/"
    print(workDir)
    log.startLogging(sys.stdout)

    ServerFactory = BroadcastServerFactory
    # ServerFactory = BroadcastPreparedServerFactory

    factory = ServerFactory(ws)
    factory.protocol = BroadcastServerProtocol
    listenWS(factory)

    webdir = File(workDir)
    web = Site(webdir)
    reactor.listenTCP(httpPort, web)
    reactor.run()


if __name__ == '__main__':
    runWebSocket("ws://0.0.0.0:9000", 9001)