'''
@author: Pratyush Verma
Date:30/Sep/2021

Description: This script performs parsing and execution of AWS jobs for Gateway app

How to run:- 1. From the terminal, navigate to the file location and type 'python3 parseMain.py' and hit enter.
             2. When jobs hit the corresponding effect will be shown.

'''


#logger ---- info, debug, warning, error
import logging
logging.basicConfig(level=0,filename='/var/tmp/parser.log',filemode='w',format='[%(asctime)s] [%(levelname)s] - %(message)s')
logger=logging.getLogger()

#conf ---
import threading
import ssl
import json
import struct
import sys
from time import sleep
#import sqlite3
import paho.mqtt.client as mqtt
import requests
import socket
import json
import subprocess
from node import *
from datetime import datetime
from configHandler import ConfigHandler
topic_name = "job/ota"

mqtt_url = 'a3qvnhplljfvjr-ats.iot.us-west-2.amazonaws.com' #url from aws
#certificates from aws
root_ca = '/etc/gateway/certUploads/root.pem'
public_crt = '/etc/gateway/certUploads/cert.pem.crt'
private_key = '/etc/gateway/certUploads/key.pem.key'

def job(client,obj,msg):
    # This callback will only be called for messages with topics that match
    # $aws/things/Test_gateway/jobs/notify-next
    logger.info("Job callback")
    logger.info(str(msg.payload))
    jobconfig = json.loads(msg.payload.decode('utf-8'))
    t_job = threading.Thread(name='parse', target=parse,args=(jobconfig,client))
    t_job.start()

def node_peripheral(task,mode,condition,mac,val,srv,ch):
    if task == "ch_write":
        print("Write Mode")
        if mode == "all":
            pass
        elif mode == "multi":
            i=0
            print("Multi device")
            for addr in mac:
                print(addr)
                try:
                    print('iiii')
                    p = Peripheral(addr,"random")
                    serv=p.getServiceByUUID(srv)
                    char=serv.getCharacteristics(ch)[0]
                    char.write(struct.pack('B',0x01))
                    print("writing char:",addr)
                    p.disconnect()
                    print('yyyy')
                except Exception as e:
                    print(e)
                    print("Exception:",addr)
                i+=1
                sleep(3)

def parse(jobconfig,client):
    confObject=ConfigHandler()
    print(jobconfig)
    if 'execution' in jobconfig:
        jobid = jobconfig['execution']['jobId']

    if jobconfig['execution']['jobdocument']['cloud']['enable']=='active':
        topic=jobconfig['execution']['jobdocument']['cloud']['topic']
        category=jobconfig['execution']['jobdocument']['cloud']['category']
        status=jobconfig['execution']['jobdocument']['cloud']['status']
        j=0
        for i in topic:
            temptopic=topic[j]
            tempcategory=category[j]
            tempstatus=status[j]
            if temptopic=='publishTopic' and tempstatus=='activate':
                confObject.updateData("cloud",{"PUBFLAG":"Active"})
            confObject.updateData("cloud",{tempcategory:temptopic})
            j+=1
        subprocess.run(['/usr/sbin/restart_script.sh'])


    if jobconfig['execution']['jobdocument']['node']['enable']=='active':
        if jobconfig['execution']['jobdocument']['node']['operation']=='write':
            mac=jobconfig['execution']['jobdocument']['node']['mac']
            service=jobconfig['execution']['jobdocument']['node']['service']
            char=jobconfig['execution']['jobdocument']['node']['char']
            data=jobconfig['execution']['jobdocument']['node']['data']
            val=[0x01]*len(mac)
            print("Value-",val)

            led_service_uuid = UUID(service)
            led_char_uuid = UUID(char)
            #node_peripheral("ch_write","multi","Null",mac,val,led_service_uuid,led_char_uuid)
            t_node = threading.Thread(name='job', target=node_peripheral,args=("ch_write","multi","Null",mac,val,led_service_uuid,led_char_uuid))
            t_node.start()
    if jobconfig['execution']['jobdocument']['gateway']['enable']=='active':
        if jobconfig['execution']['jobdocument']['gateway']['operation']=='write':
            confObject.updateData("node",{"SCAN_RATE":jobconfig['execution']['jobdocument']['gateway']['scanWindow']})
            confObject.updateData("device",{'NAME':jobconfig['execution']['jobdocument']['gateway']['deviceName']})
            confObject.updateData("device",{'SERIAL_ID':jobconfig['execution']['jobdocument']['gateway']['deviceId']})
            confObject.updateData("device",{'LOCATION':jobconfig['execution']['jobdocument']['gateway']['deviceLocatoin']})
            confObject.updateData("device",{'GROUP':jobconfig['execution']['jobdocument']['gateway']['deviceGroup']})
            subprocess.run(['/usr/sbin/restart_script.sh'])

    jobstatustopic = "$aws/things/Test_gateway/jobs/"+ jobid + "/update"
        #if operation=="publish" and cmd=="start":
        #    pubflag=True
        #elif operation=="publish" and cmd=="stop":
        #    pubflag=False
        #led config
    client.publish(jobstatustopic, json.dumps({ "status" : "SUCCEEDED"}),0)



#-------------- Main start------------------
if __name__ == "__main__":

    client = mqtt.Client()   #initialise mqtt client
    client.tls_set(root_ca,
                   certfile = public_crt,
                   keyfile = private_key,
                   cert_reqs = ssl.CERT_REQUIRED,
                   tls_version = ssl.PROTOCOL_TLSv1_2,
                   ciphers = None)
    client.message_callback_add(topic_name, job)
    client.connect(mqtt_url, port = 8883, keepalive=60)
    client.subscribe(topic_name, 0)  #subscibe to the topic
    client.loop_start()
    while True:
        print("Script started! Please wait...")
        sleep(1)
#--------------- End of script --------------
