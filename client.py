import asyncio

from autobahn.asyncio.websocket import WebSocketClientProtocol, WebSocketClientFactory

import json

import meshtastic
from pubsub import pub


import signal
import sys


class MyClientProtocol(WebSocketClientProtocol):
    def __init__(self):
        pub.subscribe(self.onReceive, "meshtastic.receive")
        pub.subscribe(self.onConnection, "meshtastci.connection.established")
        self.interface = meshtastic.SerialInterface()
        self.jsonTXT = ""

    def __del__(self):
        self.interface.close()
        print("closing serial")

    def onReceive(self, packet, interface):
        print("Serial data received")
        try:
            packet['decoded']['data']['payload'] = str(packet['decoded']['data']['payload'])
            self.jsonTXT = '{"nodes":'+json.dumps(interface.nodes)+', "packet":'+json.dumps(packet)+', "myNode":'+json.dumps(interface.getMyNodeInfo())+'}'
            print(self.jsonTXT)
            self.sendMessage(self.jsonTXT.encode("utf-8"))
        except Exception as e:
            print(e)

    def onConnection(self, interface, topic=pub.AUTO_TOPIC):
        print("serialconnect")
        #cherrypy.engine.publish('websocket-broadcast', "{'test':'connected'}")
        #interface.sendText("test hello!")

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

if __name__ == '__main__':
    factory = WebSocketClientFactory("ws://127.0.0.1:9000")
    factory.protocol = MyClientProtocol
    print("startloop")
    loop = asyncio.get_event_loop()
    coro = loop.create_connection(factory, '127.0.0.1', 9000)
    loop.run_until_complete(coro)
    loop.run_forever()
    loop.close()