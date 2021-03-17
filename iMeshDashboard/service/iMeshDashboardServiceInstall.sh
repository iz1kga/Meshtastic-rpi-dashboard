#!/bin/bash

sudo cp /usr/local/iMeshDashboard/service/iMeshDashboard.service /etc/systemd/system
sudo systemctl daemon-reload
sudo systemctl enable iMeshDashboard
sudo systemctl daemon-reload
sudo systemctl stop iMeshDashboard
sudo systemctl start iMeshDashboard
