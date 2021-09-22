# Paths
-This file consist important paths used globally

## Config
**PATH->/etc/opt/gateway/**
-Here we will store our all the configurations file
-Tree structure of the folder
gateway
    ├── current
    │   ├── cloud.conf
    │   ├── device.conf
    │   ├── node.conf
    │   └── wifi.conf
    └── default
        ├── cloud.conf
        ├── device.conf
        ├── node.conf
        └── wifi.conf

## Logging
**PATH->/var/log/gateway/**
-Here we will store all the logs of the app

## Database
**PATH->/var/lib/gateway/'offline.db'**
-Here we will store all the data which is modified frequently during run time

## Runtime
**PATH->/var/run/gateway/**
-Here we will put our data which is used during run time, from the device boot state
-State management data
