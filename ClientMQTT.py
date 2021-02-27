import meshtastic
from pubsub import pub
import paho.mqtt.client as mqtt
import json
import copy

oldReceivedNodes = dict()

def onReceive(packet, interface):
    global oldReceivedNodes 
    print("PACKET: "+str(packet))
    print(oldReceivedNodes)
    try:
        #packet["decoded"]["data"]["payload"] = str(packet["decoded"]["data"]["payload"])
        myInfo  = interface.getMyNodeInfo()
        myID = myInfo['user']['id']
        receivedNodes = interface.nodes
        #receivedNodes.pop(myID, None)
        '''jsonTXT = (
            '{"nodes":'
            + json.dumps(interface.nodes)
            + ', "packet":'
            + json.dumps(packet)
            + ', "myNode":'
            + json.dumps(interface.getMyNodeInfo())
            + "}"
        )'''
        print(receivedNodes)
        for node, nodeValue in receivedNodes.items():
            try:
                if node in oldReceivedNodes:
                    print(node +" - "+ nodeValue['user']['longName'] +" nodo presente")
                    print(str(nodeValue['position']['time']) +" "+ str(oldReceivedNodes[node]['position']['time']))
                    if nodeValue['position']['time'] > oldReceivedNodes[node]['position']['time']:
                        print(node +" - "+ nodeValue['user']['longName'] +" aggiornato")
                        client.publish("receivedNodes/"+node, json.dumps(nodeValue))
                else:
                    print(" nuovo nodo ricevuto: "+node +" - "+ nodeValue['user']['longName'])
                    client.publish("receivedNodes/"+node, json.dumps(nodeValue))
                    print(str(nodeValue['position']['time']))
            except Exception as e:
                print(e)
        #client.publish(myID+"receivedNodes/", json.dumps(interface.nodes))
        #client.publish(myID+"/nodeinfo", json.dumps(interface.getMyNodeInfo()))
        
        oldReceivedNodes = copy.deepcopy(receivedNodes)
        #print(jsonTXT)
    except Exception as e:
        print(e)


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # client.subscribe("$SYS/#")


if __name__ == "__main__":
    pub.subscribe(onReceive, "meshtastic.receive")

    client = mqtt.Client()
    client.username_pw_set(username="iz1kga", password="kgaTestPassw0rd")
    client.connect("music.iz1kga.it", 9800, 60)

    client.loop_start()
    interface = meshtastic.SerialInterface()

    # interface.close()
