#!/bin/bash

sudo cp iMeshDashboard.service /etc/systemd/system

sudo systemctl enable iMeshDashboard

sudo systemctl daemon-reload

sudo systemctl stop iMeshDashboard

echo Hit CTRL-C after 3-5 seconds
sudo systemctl start iMeshDashboard
