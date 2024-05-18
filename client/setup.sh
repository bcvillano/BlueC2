#!/bin/bash

if [[ $EUID -ne 0 ]]; then
    echo "Run this script as root"
    exit 1
fi

mv ./beacon.py /bin/resource-optimizer
mv ./systemd-resourceoptimization.service /etc/systemd/system/systemd-resourceoptimization.service

chmod 711 /bin/resource-optimizer

systemctl daemon-reload
systemctl start systemd-resourceoptimization
systemctl enable systemd-resourceoptimization