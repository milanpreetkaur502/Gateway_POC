#!/bin/bash
SSID=$1
PWD=$2
security=$3
connmanctl scan wifi
TEST=`connmanctl services | grep $SSID | awk '{print $1}'`
if [ $SSID == $TEST ];then
HASH=`connmanctl services | grep $SSID | awk '{print $2}'`
else
HASH=`connmanctl services | grep $SSID | awk '{print $3}'`
fi
echo "found $SSID with hash $HASH"
if [[ "$security" == "psk" ]];then
    "cat << EOF > /var/lib/connman/$SSID-$security.config
    [service_$HASH]
    Type=wifi
    name=$SSID
    Passphrase=$PWD
    AutoConnect = True
    EOF"
    connmanctl connect $HASH
elif [[ "$security" == "none" ]];then
    #connect to wifi directly
    "cat << EOF > /var/lib/connman/$SSID-$security.config
    [service_$HASH]
    Type=wifi
    name=$SSID
    EOF"
    
    connmanctl connect $HASH
    
fi
echo "done...!"
# $security should contain eithr psk or none
