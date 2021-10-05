'''
@author: Rohit
Date:28/Sep/2021

Description: This script performs OTA on application level. It updates the scripts 
             automatically using Jobs comming from aws.

How to run:- 1. Go to terminal and type 'python3 OTA_main.py' and hit enter.
             2. It will show 'Script updated successfully' message in terminal
                when a job hits.

'''

import json
import subprocess
import ssl
import paho.mqtt.client as mqtt
from time import sleep
from bluepy.btle import Scanner, DefaultDelegate , UUID, Peripheral
from time import sleep
import struct
import sys
import threading


topic_name = "job/ota"

mqtt_url = 'a3qvnhplljfvjr-ats.iot.us-west-2.amazonaws.com' #url from aws
#certificates from aws
root_ca = '/home/lab/pythonble/BLE/certUploads/root.pem'   
public_crt = '/home/lab/pythonble/BLE/certUploads/cert.pem.crt'  
private_key = '/home/lab/pythonble/BLE/certUploads/key.pem.key'

#---------------node------------------------

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
                
    
#----------------------------------------------    

#-------------- Parsing -------------------
def ota_parse(client, obj, msg):
    print('job hit')
    print(str(msg.payload))
    jobconfig = json.loads(msg.payload.decode('utf-8'))

    operation = jobconfig['operation']
    mac = jobconfig['mac']
    service = jobconfig['service']
    char = jobconfig['char']
    print('received mac',mac)
    '''
    #scanner = Scanner(0)
    #devices = scanner.scan(3)
    #dev_addr=[]   # store MAC
              
    for dev in devices:
        dev_name=dev.getValueText(9) # extracting adv packet with type id 9 for local name field
        if dev_name=='Tag':
            dev_addr.append(dev.addr)

    print(dev_addr)
    print("Device Count-",len(dev_addr))
    '''
    val=[0x01]*len(mac)
    print("Value-",val)

##Reference Service and Charatertistic ID variable for led control
    led_service_uuid = UUID(service)
    led_char_uuid = UUID(char)


#Creating peripheral devices (Need to make it dynamic)

    #node_peripheral("ch_write","multi","Null",mac,val,led_service_uuid,led_char_uuid)
    t_job = threading.Thread(name='job', target=node_peripheral,args=("ch_write","multi","Null",mac,val,led_service_uuid,led_char_uuid))
    t_job.start()


    print("DONE")
#-------------------------------------------



#-------------- Main start------------------
if __name__ == "__main__":

    client = mqtt.Client()   #initialise mqtt client
    client.tls_set(root_ca,
                   certfile = public_crt,
                   keyfile = private_key,
                   cert_reqs = ssl.CERT_REQUIRED,
                   tls_version = ssl.PROTOCOL_TLSv1_2,
                   ciphers = None)
    client.message_callback_add(topic_name, ota_parse)
    client.connect(mqtt_url, port = 8883, keepalive=60)
    client.subscribe(topic_name, 0)  #subscibe to the topic
    client.loop_start()
    while True:
        print("Script started! Please wait...")
        sleep(1)
#--------------- End of script --------------
