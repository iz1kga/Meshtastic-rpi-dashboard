from flask import Flask, render_template, request, send_from_directory, url_for, redirect
from flask_basicauth import BasicAuth
import requests
import json
import copy
import atexit
import time

import paho.mqtt.client as mqtt

import meshtastic
from pubsub import pub

from waitress import serve

oldReceivedNodes = dict()
receivedNodes = dict()
myNodeInfo = dict()

app = Flask(__name__)

app.config['BASIC_AUTH_USERNAME'] = 'user'
app.config['BASIC_AUTH_PASSWORD'] = 'password'
app.config['BASIC_AUTH_FORCE'] = True

basic_auth = BasicAuth(app)

def updateImeshMap():
    global oldReceivedNodes
    global receivedNodes
    receivedNodes = copy.deepcopy(interface.nodes)
    try:
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
        oldReceivedNodes = copy.deepcopy(receivedNodes)
        #print(jsonTXT)
    except Exception as e:
        print(e)

def getFloat(fnum):
    if isinstance(fnum, float):
        return "{:.4f}".format(fnum)
    else:
        return ""

def getNodes():
    nodesList = []
    for node, value in receivedNodes.items():
        print(value)
        if 'position' in value:
            pos = getFloat(value['position'].get('latitude')) +", "+getFloat(value['position'].get('longitude')) + ", " + str(value['position'].get('altitude'))
            lh = value['position'].get('time', "")
            batt = value['position'].get('batteryLevel', "")
        else:
            pos = ""
            lh = ""
            batt = ""
        nodesList.append({"user":value['user']['longName'], "id":node, "pos":pos, "lh":lh, "batt":batt, "snr":value.get('snr', "")})
    return(json.dumps(nodesList))

def getNodeInfo():
    global myNodeInfo
    myNodeInfo = interface.getMyNodeInfo()
    return json.dumps(myNodeInfo)

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)
@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('css', path)

@app.route('/')
def index():
    getNodes()
    return render_template('index.html', nodes=getNodes(), nodeInfo=getNodeInfo())

@app.route('/getNodes')
def printNodes():
    return getNodes()

@app.route('/getNodeInfo')
def printNodeInfo():
    return getNodeInfo()

@app.route('/sendMessage', methods=['POST'])
def sendMessage():
    if request.method == 'POST':
        msg = request.form['fmsg']
        interface.sendText(msg, wantAck=True)
    return redirect(url_for('index'))

@app.route('/setNode', methods=['POST'])
def setData():
    if request.method == 'POST':
        interface.setOwner(request.form['flongName'])
        prefs = interface.radioConfig.preferences
        alt = int(request.form['faltitude'])
        lat = float(request.form['flatitude'])
        lon = float(request.form['flongitude'])
        ts = int(time.time())
        prefs.fixed_position = True
        interface.sendPosition(lat, lon, alt, ts)
        interface.writeConfig()  
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
    form = LoginForm()
    if form.validate_on_submit():
        # Login and validate the user.
        # user should be an instance of your `User` class
        login_user(user)

        flask.flash('Logged in successfully.')

        next = flask.request.args.get('next')
        # is_safe_url should check if the url is safe for redirects.
        # See http://flask.pocoo.org/snippets/62/ for an example.
        if not is_safe_url(next):
            return flask.abort(400)

        return flask.redirect(next or flask.url_for('index'))
    return flask.render_template('login.html', form=form)


if __name__ == '__main__':
    interface = meshtastic.SerialInterface()
    client = mqtt.Client()
    client.username_pw_set(username="iz1kga", password="kgaTestPassw0rd")
    client.connect("music.iz1kga.it", 9800, 60)
    client.loop_start()
    updateImeshMap()
    getNodeInfo()
    pub.subscribe(updateImeshMap, "meshtastic.receive")
    atexit.register(lambda: interface.close)
    serve(app, host='0.0.0.0', port='5000')
    #app.run(debug=False, use_reloader=False)

    