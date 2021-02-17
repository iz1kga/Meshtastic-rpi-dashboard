from ws4py.client import WebSocketBaseClient

import json

import meshtastic
from pubsub import pub


import signal
import sys

def signal_handler(signal, frame):
    interface.close()
    sys.exit(0)

def onReceive(packet, interface):
    try:
        packet['decoded']['data']['payload'] = str(packet['decoded']['data']['payload'])
        jsonTXT = '{"nodes":'+json.dumps(interface.nodes)+', "packet":'+json.dumps(packet)+'}'
        print(jsonTXT)
        ws.send(jsonTXT)
    except Exception as e:
        print(e)
    #ws.send(json.dumps(packet))

def onConnection(interface, topic=pub.AUTO_TOPIC):
    print("serialconnect")
    #cherrypy.engine.publish('websocket-broadcast', "{'test':'connected'}")
    #interface.sendText("test hello!")
    ws.send("")


signal.signal(signal.SIGINT, signal_handler)


ws = WebSocketBaseClient('ws://localhost:9000/ws')
ws.connect()

pub.subscribe(onReceive, "meshtastic.receive")
pub.subscribe(onConnection, "meshtastci.connection.established")


interface = meshtastic.SerialInterface()
