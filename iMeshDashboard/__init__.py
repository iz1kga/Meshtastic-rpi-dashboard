#!/usr/bin/env python3
from flask import Flask, render_template, request, send_from_directory, url_for, redirect
from flask_basicauth import BasicAuth
from flask_apscheduler import APScheduler
import requests
import json
import copy
import atexit
import time
import timeago
from datetime import datetime
import paho.mqtt.client as mqtt
import meshtastic
from meshtastic import remote_hardware, portnums_pb2, remote_hardware_pb2

from pubsub import pub
import configparser
from pkg_resources import get_distribution, DistributionNotFound
import os.path

try:
    _dist = get_distribution('iMesh-Dashboard')
except DistributionNotFound:
    __version__ = 'Unknown version'
else:
    __version__ = _dist.version

dataPath = '/usr/local/iMeshDashboard'
config = configparser.ConfigParser()
config.read(dataPath+'/conf/app.conf')

from waitress import serve

oldReceivedNodes = dict()
receivedNodes = dict()
myNodeInfo = dict()
mapNodes = []

positionBeacon = False


interface = meshtastic.SerialInterface()

client = mqtt.Client()
client.username_pw_set(username=config['MQTT']['username'], password=config['MQTT']['password'])

app = Flask(__name__, template_folder=dataPath+'/templates')

app.config['BASIC_AUTH_USERNAME'] = config['AUTH']['username']
app.config['BASIC_AUTH_PASSWORD'] = config['AUTH']['password']

basic_auth = BasicAuth(app)

appData = {"version":__version__}

def sendPosition():
    print("Sending Position Beacon")
    interface.sendPosition(float(config['Position']['lat']), float(config['Position']['lon']), int(config['Position']['alt']), int(time.time()))

def getNodeInfo():
    global myNodeInfo
    myNodeInfo = interface.getMyNodeInfo()
    return json.dumps(myNodeInfo)

def getMapNodeInfo(node):
        tDelta = int(time.time()) - int(node['position']['time'])
        color = "indigo"
        if(tDelta <= 172800):
            color = "purple"
        if(tDelta <= 86400):
            color = "red"
        if(tDelta <= 43200):
            color = "coral"
        if(tDelta <= 21600):
            color = "orange"
        if(tDelta <= 10800):
            color = "yellowgreen"
        if(tDelta <= 3600):
            color = "green"
        textContent = ("<div><h4>"+node['user']['longName']+"</h4><table>"
                      "<tr><td>Id:</td><td>"+node['user']['id']+"<td></tr>"
                      "<tr><td>Position:</td><td>"+getFloat(node['position']['latitude'])+"°, "+getFloat(node['position']['longitude'])+"°,"
                      " "+str(node['position'].get('altitude', '--'))+"m<td></tr>"
                      "<tr><td>Last Heard:</td><td>"+getLH(node['position']['time'])+"<td></tr>"
                      "<tr><td></td><td>"+getTimeAgo(node['position']['time'])+"<td></tr>"
                      "</table></div>")
        return color, textContent

def onGPIOreceive(interface, packet):
    print("remote_hardware")
    print(packet)
    pb = remote_hardware_pb2.HardwareMessage()
    pb.ParseFromString(packet["decoded"]["data"]["payload"])
    print(pb)
    print(f"Received RemoteHardware typ={pb.typ}, gpio_value={pb.gpio_value}")

def updateImeshMap(interface, packet):
    global oldReceivedNodes
    global receivedNodes
    global mapNodes
    mapNodes = []
    receivedNodes = copy.deepcopy(interface.nodes)

    if packet is not None:
        print("Packet received:")
        print(packet)
        hop = packet.get('hopLimit', None)
        print(hop)
        if (hop is not None) and (myNodeInfo['user']['id'] != packet.get('fromId')):
            print("Pushing received node info")
            client.publish("meshInfo/hopInfo", json.dumps({"receivedNode":packet.get('fromId'), "receiverNode":myNodeInfo['user']['id'],
                           "hopLimit":packet.get('hopLimit'), "rxTime":packet.get('rxTime')}))
    try:
        for node, nodeValue in receivedNodes.items():
            try:
                mapNodes.append([nodeValue['user']['longName'], nodeValue['position']['latitude'],
                                 nodeValue['position']['longitude'], getMapNodeInfo(nodeValue)[0], getMapNodeInfo(nodeValue)[1], getHourDiff(nodeValue['position']['time'])])
                if node in oldReceivedNodes:
                    print(node +" - "+ nodeValue['user']['longName'] +" nodo presente")
                    if nodeValue['position']['time'] > oldReceivedNodes[node]['position']['time']:
                        print("aggiornato")
                        client.publish("receivedNodes/"+node, json.dumps(nodeValue))
                else:
                    print(" nuovo nodo ricevuto: "+node +" - "+ nodeValue['user']['longName'])
                    if(config['MQTT']['enabled']=="True"):
                        client.publish("receivedNodes/"+node, json.dumps(nodeValue))
                    print(str(nodeValue['position'].get('time')))
            except Exception as e:
                print(e)
        oldReceivedNodes = copy.deepcopy(receivedNodes)
    except Exception as e:
        print(e)

def getHourDiff(TS):
    return int((int(time.time())-int(TS))/3600)

def getFloat(fnum):
    if isinstance(fnum, float):
        return "{:.4f}".format(fnum)
    else:
        return ""

def getLH(ts, default=""):
    return datetime.fromtimestamp(ts).strftime('%d-%m-%Y %H:%M:%S') if ts else default

def getTimeAgo(ts, default=""):
    return timeago.format(datetime.fromtimestamp(ts), datetime.now()) if ts else default

def getNodes():
    nodesList = []
    for node, value in receivedNodes.items():
        if (value['user']['id'] == myNodeInfo['user']['id']):
            continue
        if 'position' in value:
            lhTS = value['position'].get('time')
            if (lhTS is None) or (lhTS < (int(time.time())-86400)):
                continue
            if 'latitude' in value['position'] and 'longitude' in value['position']:
                pos = getFloat(value['position'].get('latitude')) +"°, "+getFloat(value['position'].get('longitude')) + "°, " + str(value['position'].get('altitude', '---'))+"m"
            else:
                pos=""
            lh = getLH(lhTS)
            since = getTimeAgo(lhTS)
            batt = str(value['position'].get('batteryLevel', ""))
            batt = batt + ("%" if (batt != "") else "")
        else:
            pos = ""
            since = ""
            lh = ""
            batt = ""

        snr = str(value.get('snr'))
        snr = snr + (" dB" if (snr != "") else "")
        nodesList.append({"user":value['user']['longName'], "id":node, "pos":pos, "lh":lh, "batt":batt, "snr":snr, "since":since})
        nodesList = sorted(nodesList, key=lambda k: k['lh'], reverse=True)
    return(json.dumps(nodesList))



@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory(dataPath+'/js', path)
@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory(dataPath+'/css', path)
@app.route('/img/<path:path>')
def send_img(path):
    return send_from_directory(dataPath+'/img', path)

@app.route('/')
def indexPage():
    getNodes()
    return render_template('index.html', Title="iMesh Node Landing Page", 
                                         nodeInfo=myNodeInfo, info=interface.myInfo, appData=appData)

@app.route('/lh')
def lhPage():
    getNodes()
    return render_template('lh.html', Title="Last Heard", 
                                      nodeInfo=myNodeInfo, appData=appData)

@app.route('/map')
def mapPage():
    getNodes()
    return render_template('map.html', nodesList=mapNodes, Title="Nodes Map", 
                                       nodeInfo=myNodeInfo, appData=appData)

@app.route('/private/config')
@basic_auth.required
def configPage():
    getNodes()
    return render_template('config.html', Title="Nodes Map", 
                                          nodeInfo=myNodeInfo, appData=appData, nodes=receivedNodes.items())

@app.route('/getNodes')
def printNodes():
    return getNodes()

@app.route('/getNodeInfo')
def printNodeInfo():
    return getNodeInfo()

@app.route('/sendMessage', methods=['POST'])
@basic_auth.required
def sendMessage():
    if request.method == 'POST':
        msg = request.form['fmsg']
        interface.sendText(msg, wantAck=True)
    return redirect(url_for('configPage'))

@app.route('/setNode', methods=['POST'])
@basic_auth.required
def setNode():
    if request.method == 'POST':
        interface.waitForConfig()
        interface.setOwner(request.form['flongName'],  request.form['fshortName'])
        interface.waitForConfig()
        prefs = interface.radioConfig.preferences
        alt = int(request.form['faltitude'])
        lat = float(request.form['flatitude'])
        lon = float(request.form['flongitude'])
        ts = int(time.time())
        if not interface.myInfo.has_gps and not (positionBeacon):
            prefs.fixed_position = True
            interface.sendPosition(lat, lon, alt, ts)
            interface.waitForConfig()
            interface.writeConfig()
        else:
            print("Cannot set node parameters beacuse has gps: %s or has fixed position config in config file: %s" % 
                   (interface.myInfo.has_gps, (positionBeacon),))
    return redirect(url_for('configPage'))

@app.route('/setGpio', methods=['POST'])
@basic_auth.required
def setGpio():
    if request.method == 'POST':
        tId = request.form['fTarget']
        tGpio = int(request.form['fGpio'])
        tValue = int(request.form['fValue'])
        bitmask = 0
        bitval = 0
        bitmask |= 1 << tGpio
        bitval |= tValue << tGpio
        r = remote_hardware_pb2.HardwareMessage()
        r.typ = remote_hardware_pb2.HardwareMessage.Type.WRITE_GPIOS
        r.gpio_mask = bitmask
        r.gpio_value = bitval
        interface.sendData(r, tId, portnums_pb2.REMOTE_HARDWARE_APP, wantAck = True)
        print(f"Writing GPIO mask 0x{bitmask:x} with value 0x{bitval:x} to {tId}")
    return redirect(url_for('configPage'))
    

@app.route('/getGpio')
@basic_auth.required
def getGpio():
    if request.method == 'GET':
        tId = request.args.get('target')
        tGpio = int(request.args.get('gpio'))
        bitmask = 0
        bitmask |= 1 << tGpio
        r = remote_hardware_pb2.HardwareMessage()
        r.typ = remote_hardware_pb2.HardwareMessage.Type.READ_GPIOS
        r.gpio_mask = bitmask
        interface.sendData(r, tId, portnums_pb2.REMOTE_HARDWARE_APP, wantAck = True)
    #return redirect(url_for('configPage'))
    return (tId+" "+str(tGpio)+" "+hex(bitmask))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        login_user(user)

        flask.flash('Logged in successfully.')

        next = flask.request.args.get('next')
        if not is_safe_url(next):
            return flask.abort(400)

        return flask.redirect(next or flask.url_for('indexPage'))
    return flask.render_template('login.html', form=form)

def main():
    global positionBeacon
    print("Starting iMeshDashboard v%s" % (__version__,))

    print("MQTT ENABLED: %s" % config['MQTT']['enabled'])
    scheduler = APScheduler()
    if ("Position" in config) and (config['Position']['enabled']=='True'):
        print("Position Beacon Enabled")
        positionBeacon = True
    if(positionBeacon):
        print("Setting postition info")
        scheduler.add_job(func=sendPosition, trigger='interval', id='sendPos', seconds=int(config['Position']['interval']))
        interface.sendPosition(float(config['Position']['lat']), float(config['Position']['lon']), int(config['Position']['alt']), int(time.time()))
        interface.waitForConfig()
        interface.writeConfig()
    scheduler.start()

    if(config['MQTT']['enabled']=="True"):
        client.connect(config['MQTT']['host'], int(config['MQTT']['port']), int(config['MQTT']['keepalive']))
        client.loop_start()
    getNodeInfo()
    updateImeshMap(interface, None)
    pub.subscribe(updateImeshMap, "meshtastic.receive")
    pub.subscribe(onGPIOreceive, "meshtastic.receive.data.REMOTE_HARDWARE_APP")
    atexit.register(lambda: interface.close())
    serve(app, host=config['NET']['bind'], port=config['NET']['port'])
    #only for debug!
    #app.run(debug=True, use_reloader=False)

if __name__ == '__main__':
    main()
