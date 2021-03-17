#!/bin/bash

sudo cp iMeshDashboard.service /etc/systemd/system
sudo systemctl enable iMeshDashboard
sudo systemctl daemon-reload
sudo systemctl stop iMeshDashboard
sudo systemctl start iMeshDashboard
