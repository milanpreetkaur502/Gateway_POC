#!/bin/bash

path='/home/commlab/Documents/Gateway_POC-test/autoRestart/main_app.service'

#enable it as a service first
sudo systemctl daemon-reload
sudo systemctl enable $path

#start a srvice
#sudo systemsctl start $path

#restart a service
sudo systemctl restart $path

