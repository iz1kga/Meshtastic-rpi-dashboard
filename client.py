import urllib.request, json 
from datetime import datetime

from autobahn.twisted.websocket import WebSocketClientProtocol, WebSocketClientFactory
from twisted.internet import reactor, task
from twisted.python import log

import sys, os

import meshtastic
from pubsub import pub

import signal

from daemons.prefab import run

import configparser

class MyClientProtocol(WebSocketClientProtocol):
    def __init__(self, ):
        super().__init__()
        import configparser
        self.config = configparser.ConfigParser()
        self.configPath = os.path.dirname(__file__)+'/client.conf'
        print(self.configPath)
        self.config.read(self.configPath)
        print(self.config.sections())
        self.interface = meshtastic.SerialInterface()
        pub.subscribe(self.onReceive, "meshtastic.receive")
        self.jsonTXT = ""
        if "TORINOMETEO" in self.config:
            self.l = task.LoopingCall(self.getMeteoTM)
            self.l.start(float(self.config['TORINOMETEO']['updateTime']))
        if "BEACON" in self.config:
            self.b = task.LoopingCall(self.sendBeacon)
            self.b.start(float(self.config['BEACON']['updateTime']), False)

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

    def getMeteoTM(self):
        with urllib.request.urlopen("https://www.torinometeo.org/api/v1/realtime/data/"+self.config['TORINOMETEO']['slug']) as url:
            data = json.loads(url.read().decode())
            print(data['temperature'])
            self.interface.sendText("Stazione "+data['station']['name']+
                                    "\nTemperatura: "+data['temperature']+
                                    "°C\nUmidità: "+data['relative_humidity']+
                                    "%\nPressione: "+data['pressure']+"mbar"+
                                    "\nwww.torinometeo.org",
                                    wantAck=True)
    def sendBeacon(self):
        self.interface.sendText(self.config['BEACON']['text'], wantAck=True)

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
