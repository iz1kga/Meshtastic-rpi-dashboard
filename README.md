# Meshtastic-rpi-dashboard
## Setup:

`git clone https://github.com/iz1kga/Meshtastic-rpi-dashboard.git`
`cd Meshtastic-rpi-dashboard`
`sudo pip3 install -r requirements.txt`

## Run / stop / restart:
### Server
`./dashboard startServer|stopServer|restartServer`
this will run the websocket server

### Serial and websocket client
`./dashboard startClient|stopClient|restartClient`
this will run the client that will connect to the board via serial usb and to the websocket server pushing updates received from serial

### Websocket webclient
in ./webClient/ folder there are all the files needed for the webclient. It's possible to run locally opening the index.htm in the browser or uploating to a webserver.

#### Local Run
The `./dassboard runServer` command starts both webserver and websocket Server the websocket is available at port 9000 the webserver at port 9001

You cant get the dashboard locally at http://localhost:9001/

#### Remote Run
Fully configurable service suite will be provided soon, server client and webclient have te ability to run on different machines

## Configuration
### Client

client.conf configuration file is provided to enable and setup Serial client functionalities

#### TORINOMETEO REST API

The [TORINOMETEO] enables meteo data grab from www.torinometeo.org REST API

`slug=SELECTEDSLUG` the desired slug can be retrieved here https://www.torinometeo.org/realtime/rete/, select the dsired station, the slug is in the URL: https://www.torinometeo.org/realtime/SLUG/live
`updateTime=3600` the desired update time in seconds (a message will be sent every updateTime seconds)

#### BEACON

The [BEACON] enables send text beacon

`text=Beacon Text` Set the text that will be sent as beacon
`updateTime=1500` Time in seconds, when this amount of time is elapsed te beacon is sent

### Disclaimer

This software is experimental and I've still not considered all cyber security implication. Please Avoid unauthorized persons to acces your systems!
