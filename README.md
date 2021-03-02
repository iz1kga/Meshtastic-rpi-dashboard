# Meshtastic-rpi-dashboard
### Create Dashboard for serial connected meshtastic device

## Setup:
`sudo pip3 install iMesh-Dashboard`

## Configuration

Edit /usr/local/iMeshDashboard/conf/app.conf

```
[AUTH] #authentication for dashboard
username=user
password=testPassword

[NET] # binding address and port for dashboard
bind=0.0.0.0
port=5000

[MQTT] #mqtt server for publishing received nodes (i use it to render imeshmap.iz1kga.it)
host=mqtt.test.org
port=1883
username=MQTTuser
password=MQTTpassword
keepalive=60
enabled=True #set False i you dont want to publish to MQTT
```

## Run
from console run `iMeshDashboard`, right now I'm using screen to keep daskbaord running... I've to find a better way to do that, but I'm not so skilled so... be patient

### Disclaimer

This software is experimental. Please Avoid unauthorized persons to acces your systems!
