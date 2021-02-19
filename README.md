# Meshtastic-rpi-dashboard
## Setup:

`git clone https://github.com/iz1kga/Meshtastic-rpi-dashboard.git`
`cd Meshtastic-rpi-dashboard`
`sudo pip3 install -r requirements.txt`

## Run:
### Server
`python3 server.py`
this will run the websocket server

### Serial and websocket client
`python3 client.py`
this will run the client that will connect to the board via serial usb and to the websocket server pushing updates received from serial

### Websocket webclient
in ./webClient/ folder there are all the files needed for the webclient. It's possible to run locally opening the index.htm in the browser or uploating to a webserver.

### Disclaimer

This software is experimental and I've still not considered all cyber security implication. Please Avoid unauthorized persons to acces your systems!