import paho.mqtt.client as mqtt
from collections import deque
from gatewayapp.cloud import *
from gatewayapp.node import *
from datetime import datetime

from  gatewayapp.configHandler import ConfigHandler
import time
import threading

import logging
logging.basicConfig(level=0,filename='/var/tmp/main.log',filemode='w',format='[%(asctime)s] [%(levelname)s] - %(message)s')
logger=logging.getLogger()

def cloud():
    print("CLOUD Started")
    global client

    while True:
        chgEvent.wait()
        if len(q)!=0 and C_STATUS=='Active' and N_STATUS=='Active':#and I_STATUS=='Active':
            d = q.popleft()
            for dev in d:
                dt={}
                now=datetime.now()
                dt = {'t_stmp' : int(datetime.timestamp(now)),
                    't_utc' : now.strftime("%d/%m/%Y, %H:%M:%S"),
                    'value' : dev['value'],
                    'sensorType' : dev['sensorType'],
                    'MAC' : dev['MAC'],
                    'MACTYPE' : dev['MACTYPE'],
                    'RSSI' : dev['RSSI']
                    }

                if SERVER_TYPE == 'custom':
                    publishData(client,dt,TOPIC,'True',mainBuffer,SERVER_TYPE,STORAGEFLAG,LOGGINGFLAG)
                elif SERVER_TYPE == 'aws':
                    publishData(client,dt,TOPIC,PUBFLAG,mainBuffer,SERVER_TYPE,STORAGEFLAG,LOGGINGFLAG)
        time.sleep(0.01)

def dbMaster():
    print("DB Started")
    while True:
        if len(mainBuffer['dbCmnd'])!=0:
            job=mainBuffer['dbCmnd'].popleft()
            source=job['source']
            table=job['table']
            value=job['value']


            if job['operation']=='write':
                if table=='HistoricalData':
                    db.putdata(table,value)
                if table=='OfflineData':
                    db.putdata(table,value)

            if job['operation']=='update':
                if table=='Cloud':
                    db.updatetable(table,job['column'],job['value'])
                    confObject.updateData('cloud',)

        time.sleep(1)

def nodeMaster():
    logger.info("NODE STARTED")
    global SCAN_TIME
    while True:

        if C_STATUS=='Active' and N_STATUS=='Active':
            payl=app_node(int(SCAN_TIME))
            if payl!=None:
                q.append(payl)
                print(len(q))
        time.sleep(1)

#def main():



if __name__=='__main__':
    mainBuffer={'cloud':deque([]),'monitor':deque([]),'dbCmnd':deque([]),'nodeCmnd':deque([])}
    confObject=ConfigHandler()
    confData=confObject.getDataForMain()
    q=deque()
    que=[]
    #-------------------- GLOBAL VARIABLES  ------------------------------------------------------------
    global ID
    global NAME
    global PROTOCOL
    global HOST
    global PORT
    global N_STATUS
    global C_STATUS
    global BT_STATUS
    global SCAN_TIME
    global SERVER_TYPE
    global TOPIC
    global PUBFLAG
    global STORAGEFLAG
    global LOGGINGFLAG
    ID=confData['ID']
    NAME=confData['NAME']
    SERVER_TYPE=confData['SERVER_TYPE']
    HOST=confData['HOST']
    PORT=int(confData['PORT'])
    C_STATUS=confData['C_STATUS']
    TOPIC=confData['TOPIC']
    PUBFLAG=confData['PUBFLAG']
    N_STATUS=confData['N_STATUS']
    SCAN_TIME=confData['SCAN_TIME']
    STORAGEFLAG=confData['STORAGEFLAG']
    LOGGINGFLAG=confData['LOGGINGFLAG']
    I_STATUS=''    #why these variables are here
    BT_STATUS=''
    print("SERVER_TYPE->",SERVER_TYPE)
    print("HOST->",HOST)
    print("PORT->",PORT)
    print("C_STATUS->",C_STATUS)
    print("TOPIC->",TOPIC)
    print("PUBFLAG->",PUBFLAG)
    print("N_STATUS->",N_STATUS)
    print("SCAN_TIME->",SCAN_TIME)
    print("LOGGINGFLAG->",LOGGINGFLAG)
    print("STORAGEFLAG->",STORAGEFLAG)

    if STORAGEFLAG=='Active' and LOGGINGFLAG=='Active':
        from gatewayapp.database import p1 as db

    #-------------------------------------------------------------------------------------------------

    #-------  THREAD Section ----------------------------------------------------------------------
    conEvent=threading.Event()
    monEvent=threading.Event()
    chgEvent=threading.Event()
    if STORAGEFLAG=='Active' and LOGGINGFLAG=='Active':
        t_dbMaster=threading.Thread(name='dbMaster', target=dbMaster)
        t_dbMaster.start()
    t_nodeMaster=threading.Thread(name='nodeMaster', target=nodeMaster)
    t_nodeMaster.start()
    t_cloud=threading.Thread(name='cloud', target=cloud)
    t_cloud.start()
    #-------------------------------------------------------------------------------------------------

    #-------  MAIN THREAD Section --------------------------------------------------------------------
    prev_HOST=''
    prev_PORT=''
    while True:
        if prev_HOST!=HOST or prev_PORT!=PORT:
            print("-"*20)
            print("Server setting")
            if chgEvent.isSet():
                chgEvent.clear()
            if connflag==True:
                client.loop_stop()
                client.disconnect()
            client = mqtt.Client()
            print("Connecting to cloud...")
            funInitilise(client,SERVER_TYPE,HOST,PORT)
            prev_HOST=HOST
            prev_PORT=PORT
            if SERVER_TYPE == 'aws':
                client.subscribe("$aws/things/Test_gateway/jobs/notify-next",1)
            client.loop_start()
            chgEvent.set()
            print("-"*20)
        time.sleep(1)
    #-------------------------------------------------------------------------------------------------
