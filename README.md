# Meshtastic-rpi-dashboard
### Create Dashboard for serial connected meshtastic device

## Setup:
`sudo pip3 install iMesh-Dashboard`

## Configuration

#### First installation
```
cd /usr/local/iMeshDashboard/conf/
sudo mv app.conf.example app.conf
sudo nano app.conf
```

#### Configuration example
```
[AUTH] #authentication for dashboard
username=user
password=testPassword

[NET] # binding address and port for dashboard
bind=0.0.0.0
port=5000

[Position] # send position beacon for non gps devices
lat=45.5
lon=7.5
alt=250
interval=375
enabled=False

[MQTT] #mqtt server for publishing received nodes (i use it to render imeshmap.iz1kga.it)
host=mqtt.test.org
port=1883
username=MQTTuser
password=MQTTpassword
keepalive=60
enabled=False
```

## Run
Install systemd service running: 
```sudo /usr/local/iMeshDashboard/service/iMeshDashboardServiceInstall.sh```
the service will start at end of installation

control service:
```
systemctl start iMeshDashboard
systemctl stop iMeshDashboard
systemctl status iMeshDashboard
```

### Disclaimer

This software is experimental. Please Avoid unauthorized persons to acces your systems!
