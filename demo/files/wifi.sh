#!/bin/bash
​
SSID=$1
PWD=$2
security=$3
​
connmanctl scan wifi
TEST=`connmanctl services | grep $SSID | awk '{print $1}'`
​
if [ $SSID == $TEST ];then
HASH=`connmanctl services | grep $SSID | awk '{print $2}'`
else
HASH=`connmanctl services | grep $SSID | awk '{print $3}'`
fi
echo "found $SSID with hash $HASH"
​
​
if [[ $security == "psk" ]];then
    
    echo "[service_$HASH]
    Type=wifi
    Name=$SSID
    Passphrase=$PWD
    AutoConnect = True" > /var/lib/connman/$SSID-psk.config
​
    connmanctl connect $HASH
​
elif [[ $security == "none" ]];then
    
    echo "[service_$HASH]
    Type=wifi
    Name=$SSID
    AutoConnect = True" > /var/lib/connman/$SSID-none.config
    
    connmanctl connect $HASH
    
fi
​
echo "done...!"
​
​
# $security should contain eithr psk or none
