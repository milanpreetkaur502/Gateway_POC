#!/bin/bash
​
a=`jq '.network.SSID' /etc/gateway/config.conf`
b=`jq '.network.PASSPHRASE' /etc/gateway/config.conf`
c=`jq '.network.SECURITY' /etc/gateway/config.conf`


wifissid=`echo $a | sed 's/^.//' | sed 's/.$//'`
wifipassword=`echo $b | sed 's/^.//' | sed 's/.$//'`
wifisecurity=`echo $c | sed 's/^.//' | sed 's/.$//'`
​
connmanctl scan wifi
TEST=`connmanctl services | grep $wifissid | awk '{print $1}'`
​
if [[ $wifissid == $TEST ]];then
HASH=`connmanctl services | grep $wifissid | awk '{print $2}'`
else
HASH=`connmanctl services | grep $wifissid | awk '{print $3}'`
fi
echo "found $wifissid with hash $HASH"
​
​
if [[ $wifisecurity == "psk" ]];then
    
    echo "[service_$HASH]
    Type=wifi
    Name=$wifissid
    Passphrase=$wifipassword
    AutoConnect = True" > /var/lib/connman/$wifissid-psk.config
​
    connmanctl connect $HASH
​
elif [[ $wifisecurity == "none" ]];then
    
    echo "[service_$HASH]
    Type=wifi
    Name=$wifissid
    AutoConnect = True" > /var/lib/connman/$wifissid-none.config
    
    connmanctl connect $HASH
    
fi
​
echo "done...!"
​
​
# $security should contain eithr psk or none
