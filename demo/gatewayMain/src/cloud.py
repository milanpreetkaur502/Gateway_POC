'''
@author: Aditya Verma, Rohit Sharma
Date:28/08/2021
'''
#import paho.mqtt.client as mqtt
import ssl, random
import time
import json
import sys
import requests
from datetime import datetime

#from node import app_node

path=(__file__).split('/')
path.pop()
path="/".join(path)
path=path+'/certUploads/'
print(path)

IoT_protocol_name = "x-amzn-mqtt-ca"
mqtt_url = "a3qvnhplljfvjr-ats.iot.us-west-2.amazonaws.com"
root_ca = path+'root.pem'
public_crt = path+'cert.pem.crt'
private_key = path+'key.pem.key'

connflag = False
connbflag = False  #bad connection flag
pubflag = True
awstopic="thing/1100/data"
#from database
port = 8883
server_type = 'aws'
custom_url = '3.142.131.2'


def onConnect(client, userdata, flags, response_code):
    global connflag
    global connbflag
    if response_code == 0:
        connflag = True
        print("Connected with status: {0}".format(response_code))
    else:
        print("Bad Connection", response_code)
        #connbflag = True

def onDisconnect(client, userdata, response_code):
    #logging.info("Disconnected reason " + response_code)
    client.connflag = False
    client.connbflag = True

def on_publish(client, userdata, mid):
    print(userdata + " -- " + mid)
    #client.disconnect()

def on_LedControl(client,obj,msg):
    # This callback will only be called for messages with topics that match
    # iot/led
    print("LED Control"+msg.topic+"::"+str(msg.payload)+str(type(msg.payload)))
    cmd=json.loads(msg.payload)
    print("MAC:",cmd["MAC"])
    print("CMD:",cmd["CMD"])


def on_General(client,obj,msg):
    # This callback will only be called for messages with topics that match
    # iot/general
    print("GENERAL"+msg.topic+"::"+str(msg.payload))


def funInitilise(client,SERVER_TYPE,HOST,PORT):
    print(SERVER_TYPE)
    client.on_connect = onConnect
    #client.on_disconnect = onDisconnect
    #client.on_publish = on_publish
    if SERVER_TYPE == 'custom':
        client.connect(HOST)
    elif SERVER_TYPE == 'aws':


# when the connection attempt failed it show "connection failed message"
        try:
            if int(PORT) == 8883:
                client.tls_set(root_ca,
                    certfile = public_crt,
                    keyfile = private_key,
                    cert_reqs = ssl.CERT_REQUIRED,
                    tls_version = ssl.PROTOCOL_TLSv1_2,
                    ciphers = None)

                client.connect(HOST, port = int(PORT), keepalive=60)

            elif int(PORT) == 443:
                ssl_context = ssl.create_default_context()
                ssl_context.set_alpn_protocols([IoT_protocol_name])
                ssl_context.load_verify_locations(cafile=root_ca)
                ssl_context.load_cert_chain(certfile=public_crt, keyfile=private_key)

                client.tls_set_context(context = ssl_context)
                client.connect(HOST, port = int(PORT), keepalive=60)
        except:
            print("Connection failed! Please try again...")
            exit(1)

def publishData(client, dt,t,pubflag,mainBuffer,SERVER_TYPE):
    topic=t
    if SERVER_TYPE == 'custom':
        topic = 'Msg'
        #"thing/1100/data"

    name= "BLE Gateway"
    sys_type="Gateway"
    dev_type="Beacon"
    #Sdev_id="FF:00:00:FF:AA:BB"



    t_utc = dt.get('t_utc')
    t_stmp = dt.get('t_stmp')
    mac=dt.get('MAC')
    rssi=dt.get('RSSI')
    mactype=dt.get('MACTYPE')
    value = dt.get('value')
    sensorType = dt.get('sensorType')


    msg = {
	    "Name": name,
	    "Type":sys_type,
	    "Device":dev_type,
	    "RSSI":str(rssi),
	    "IDtype":mactype,
	    "DeviceID":mac,
	    "TimestampUTC": str(t_utc),
	    "Timestamp": str(t_stmp),
	    "Sensor":sensorType,
	    "Value":str(value)

		}

    #time.sleep(5)
    #print(connflag)
    print('connflag',connflag,'pubflag',pubflag)
    if connflag == True and pubflag == 'True' and topic!='':
        print("Actually started")

        #Internet connection handling along with publishing data
        try:
            requests.head('http://www.google.com/', timeout=3)
            data=json.dumps(msg)
            rt = client.publish(topic,data,qos=2)
            print("Publishing Data...", rt)
            print(sensorType,value)
            mainBuffer['dbCmnd'].append({'table':'HistoricalData','operation':'write','value':('1',mac,rssi,str(value),str(sensorType),t_utc),'source':'cloud'})

            return True

        except requests.ConnectionError as ex:
            print("Connection Lost! Please wait for some time...")
            return False
    else:
        print("waiting...")
        mainBuffer['dbCmnd'].append({'table':'OfflineData','operation':'write','value':('1',mac,rssi,str(value),str(sensorType),t_utc),'source':'cloud'})
