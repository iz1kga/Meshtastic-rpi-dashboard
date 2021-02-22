from autobahn.twisted.websocket import WebSocketClientProtocol, WebSocketClientFactory
from twisted.internet import reactor

import sys

from twisted.python import log

import json

import meshtastic
from pubsub import pub


import signal
import sys

from daemons.prefab import run


class MyClientProtocol(WebSocketClientProtocol):
    def __init__(self, ):
        super().__init__()
        self.interface = meshtastic.SerialInterface()
        pub.subscribe(self.onReceive, "meshtastic.receive")
        self.jsonTXT = ""
    
    def __exit__(self):
        self.interface.close()

    def onReceive(self, packet, interface):
        print("Serial data received")
        try:
            packet['decoded']['data']['payload'] = str(packet['decoded']['data']['payload'])
            self.jsonTXT = '{"nodes":'+json.dumps(interface.nodes)+', "packet":'+json.dumps(packet)+', "myNode":'+json.dumps(interface.getMyNodeInfo())+'}'
            print(self.jsonTXT)
            self.sendMessage(self.jsonTXT.encode("utf-8"))
        except Exception as e:
            print(e)

    def onConnect(self, response):
        print("Server connected: {0}".format(response.peer))

    def onConnecting(self, transport_details):
        print("Connecting; transport details: {}".format(transport_details))
        return None  # ask for defaults

    def onOpen(self):
        print("WebSocket connection open.")


    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            print("Text message received: {0}".format(payload.decode('utf8')))
            try:
                cmd = json.loads(payload.decode('utf-8'))
                if(cmd.get("cmd")=="update"):
                    self.sendMessage(self.jsonTXT.encode("utf-8"))
            except Exception as e:
                print(e)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))
        self.__exit__()

class clientDaemon(run.RunDaemon):
    def run(self):
        runClient('127.0.0.1', 9000)

def runClient(host, port):
    factory = WebSocketClientFactory("ws://"+host+":"+str(port))
    
    factory.protocol = MyClientProtocol

    reactor.connectTCP(host, port, factory)
    reactor.run()   


if __name__ == '__main__':
    runClient('127.0.0.1', 9000)
