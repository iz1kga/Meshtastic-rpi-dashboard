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

### Disclaimer

This software is experimental and I've still not considered all cyber security implication. Please Avoid unauthorized persons to acces your systems!