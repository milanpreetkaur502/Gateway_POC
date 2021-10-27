'''
@author: Pratyush Verma
Date:30/Sep/2021

Description: This script performs parsing and execution of AWS jobs for Gateway app

How to run:- 1. From the terminal, navigate to the file location and type 'python3 parseMain.py' and hit enter.
             2. When jobs hit the corresponding effect will be shown.

'''


#logger ---- info, debug, warning, error
import logging
#logging.basicConfig(level=0,filename='/var/tmp/parser.log',filemode='w',format='[%(asctime)s] [%(levelname)s] - %(message)s')
#logger=logging.getLogger()

#conf ---
import threading
import ssl
import json
import struct
import sys
import time
#import sqlite3
import paho.mqtt.client as mqtt
import requests
import socket
import json
import subprocess
from node import *
from datetime import datetime
from configHandler import ConfigHandler
#----------------------------data call-------------------------
confObject=ConfigHandler()
confData=confObject.getDataForMain()
global HOST
global PORT
global SERVER_TYPE
global PUBFLAG
global C_STATUS
global LOG_TOPIC
global JOB_TOPIC
global ID
ID=confData['ID']
SERVER_TYPE=confData['SERVER_TYPE']
C_STATUS=confData['C_STATUS']
HOST=confData['HOST']
PORT=int(confData['PORT'])
PUBFLAG=confData['PUBFLAG']
LOG_TOPIC=confData['LOG_TOPIC']
JOB_TOPIC=confData['JOB_TOPIC']
print("SERVER_TYPE->",SERVER_TYPE)
print("CLOUD_STATUS->",C_STATUS)
print("HOST->",HOST)
print("PORT->",PORT)
print("PUBFLAG->",PUBFLAG)
print("JOB_TOPIC->",JOB_TOPIC)
print("LOG_TOPIC->",LOG_TOPIC)
#--------------------------------------------------------------

mqtt_url = 'a3qvnhplljfvjr-ats.iot.us-west-2.amazonaws.com' #url from aws
#certificates from aws
root_ca = '/etc/gateway/certUploads/root.pem'
public_crt = '/etc/gateway/certUploads/cert.pem.crt'
private_key = '/etc/gateway/certUploads/key.pem.key'

now=datetime.now()
time_stamp=now.strftime("%m/%d/%Y, %H:%M:%S")
def job(client,obj,msg):
    # This callback will only be called for messages with topics that match
    # $aws/things/Test_gateway/jobs/notify-next
    print("Job callback")
    print(str(msg.payload))
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
    try:
        confObject=ConfigHandler()
        print(jobconfig)
        if 'execution' in jobconfig:
            jobid = jobconfig['execution']['jobId']

        if jobconfig['execution']['jobdocument']['cloud']['enable']=='active':
            if jobconfig['execution']['jobdocument']['cloud']['operation']=="write":
                topic=jobconfig['execution']['jobdocument']['cloud']['topic']
                category=jobconfig['execution']['jobdocument']['cloud']['category']
                status=jobconfig['execution']['jobdocument']['cloud']['status']
                j=0
                if topic!="":
                    for i in topic:
                        temptopic=topic[j]
                        tempcategory=category[j]
                        tempstatus=status[j]
                        if tempcategory=='PUBLISH_TOPIC' and tempstatus=='activate':
                            confObject.updateData("cloud",{"PUBFLAG":"Active"})
                        confObject.updateData("cloud",{tempcategory:temptopic})
                        j+=1
                    #subprocess.run(['/usr/sbin/control_scripts/restart_app.sh'])
                    #subprocess.run(['/usr/sbin/control_scripts/restart_job.sh'])

            if jobconfig['execution']['jobdocument']['cloud']['operation']=="read":
                c=confObject.getData("cloud")
                client.publish(LOG_TOPIC,json.dumps(c),0)


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
                if jobconfig['execution']['jobdocument']['gateway']['scanWindow']!="":
                    confObject.updateData("node",{"SCAN_RATE":jobconfig['execution']['jobdocument']['gateway']['scanWindow']})
                if jobconfig['execution']['jobdocument']['gateway']['deviceName']!="":
                    confObject.updateData("device",{'NAME':jobconfig['execution']['jobdocument']['gateway']['deviceName']})
                if jobconfig['execution']['jobdocument']['gateway']['deviceId']!="":
                    confObject.updateData("device",{'SERIAL_ID':jobconfig['execution']['jobdocument']['gateway']['deviceId']})
                if jobconfig['execution']['jobdocument']['gateway']['deviceLocation']!="":
                    confObject.updateData("device",{'LOCATION':jobconfig['execution']['jobdocument']['gateway']['deviceLocation']})
                if jobconfig['execution']['jobdocument']['gateway']['deviceGroup']!="":
                    confObject.updateData("device",{'GROUP':jobconfig['execution']['jobdocument']['gateway']['deviceGroup']})
                #subprocess.run(['/usr/sbin/control_scripts/restart_app.sh'])
                #subprocess.run(['/usr/sbin/control_scripts/restart_job.sh'])

            if jobconfig['execution']['jobdocument']['gateway']['operation']=='read':
                d=confObject.getData("device")
                client.publish(LOG_TOPIC,json.dumps(d),0)



        jobstatustopic = "$aws/things/Test_gateway/jobs/"+ jobid + "/update"
            #if operation=="publish" and cmd=="start":
            #    pubflag=True
            #elif operation=="publish" and cmd=="stop":
            #    pubflag=False
            #led config
        client.publish(jobstatustopic, json.dumps({ "status" : "SUCCEEDED"}),0)
        client.publish(LOG_TOPIC, json.dumps({ "Timestamp" : time_stamp,"DeviceID":ID,"Source":"Job","Log":{"Msg":"Job processing finished "}}),0)
    except:
        client.publish(LOG_TOPIC, json.dumps({ "Timestamp" : time_stamp,"DeviceID":ID,"Source":"Job","Log":{"Msg":"Job processing failed! Check device logs for details."}}),0)
        print("Job processing failed! Check device logs for details.")


#-------------- Main start------------------
if __name__ == "__main__":


    prev_HOST=''
    prev_PORT=''

    client = mqtt.Client()
    l="not connected"
    while True:
        if C_STATUS=="Active" and SERVER_TYPE=="aws":

            if prev_HOST!=HOST or prev_PORT!=PORT:
                print("-"*20)
                print("Server setting")

                client.loop_stop()
                client.disconnect()


                print("Connecting to cloud...")
                client.tls_set(root_ca,certfile = public_crt,keyfile = private_key,cert_reqs = ssl.CERT_REQUIRED,tls_version = ssl.PROTOCOL_TLSv1_2,ciphers = None)
                try:
                    client.message_callback_add(JOB_TOPIC, job)
                    client.connect(HOST, PORT, keepalive=60)
                    client.subscribe(JOB_TOPIC, 0)  #subscibe to the topic
                    client.loop_start()
                    print("-"*20)
                    l='connected'
                    prev_HOST=HOST
                    prev_PORT=PORT
                    client.publish(LOG_TOPIC, json.dumps({ "Timestamp" : time_stamp,"DeviceID":ID,"Source":"Job","Log":{"Msg":"Job service started and connected to cloud.","SERVER_TYPE":SERVER_TYPE,"HOST":HOST,"PORT":PORT,"LOG_TOPIC":LOG_TOPIC}}),0)
                except Exception as e:
                    print("Error in connection!")
                    print(e)
        else:
            time.sleep(0.1)
            #print("C_STATUS not active or server not AWS")
        time.sleep(1)
        #print("Script running! Status: ",l)
#--------------- End of script --------------
