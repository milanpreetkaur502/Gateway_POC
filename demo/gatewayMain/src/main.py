import paho.mqtt.client as mqtt
from collections import deque
from gatewayapp.cloud import *
from gatewayapp.node import *
from datetime import datetime

from  gatewayapp.configHandler import ConfigHandler
import time
import threading


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
                    publishData(client,dt,PUBLISH_TOPIC,'True',mainBuffer,SERVER_TYPE,STORAGEFLAG,LOGGINGFLAG)
                elif SERVER_TYPE == 'aws':
                    publishData(client,dt,PUBLISH_TOPIC,PUBFLAG,mainBuffer,SERVER_TYPE,STORAGEFLAG,LOGGINGFLAG)
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
                if table=='HistoricalData' and STORAGEFLAG=='Active' and LOGGINGFLAG=='Active':
                    confObject.putdatacsv(value)
                if table=='OfflineData':
                    db.putdata(table,value)


        time.sleep(1)

def nodeMaster():
    print("NODE STARTED")
    global SCAN_TIME
    while True:

        if C_STATUS=='Active' and N_STATUS=='Active':
            try:
                payl,bt_status=app_node(int(SCAN_TIME))
                #print(payl)
                #print(bt_status)
                if payl!=[]:

                    q.append(payl)
                    #print(len(q))
                elif payl==[] and bt_status=="Active":
                    now=datetime.now()
                    time_stamp=now.strftime("%m/%d/%Y, %H:%M:%S")
                    client.publish(LOG_TOPIC, json.dumps({ "Timestamp" : time_stamp,"DeviceID":ID,"Source":"App","Log":{"Msg":"No active beacons found"}}),0)
                    #print("no beacons")
                elif bt_status=="Inactive":

                    #print('ble failure')
                    now=datetime.now()
                    time_stamp=now.strftime("%m/%d/%Y, %H:%M:%S")
                    client.publish(LOG_TOPIC, json.dumps({ "Timestamp" : time_stamp,"DeviceID":ID,"Source":"App","Log":{"Msg":"BLE not active"}}),0)
            except Exception as e:
                print(e)
                time.sleep(1)
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
    global PUBLISH_TOPIC
    global PUBFLAG
    global STORAGEFLAG
    global LOGGINGFLAG
    global LOG_TOPIC
    ID=confData['ID']
    NAME=confData['NAME']
    SERVER_TYPE=confData['SERVER_TYPE']
    HOST=confData['HOST']
    PORT=int(confData['PORT'])
    C_STATUS=confData['C_STATUS']
    PUBLISH_TOPIC=confData['PUBLISH_TOPIC']
    PUBFLAG=confData['PUBFLAG']
    N_STATUS=confData['N_STATUS']
    SCAN_TIME=confData['SCAN_TIME']
    STORAGEFLAG=confData['STORAGEFLAG']
    LOGGINGFLAG=confData['LOGGINGFLAG']
    LOG_TOPIC=confData['LOG_TOPIC']
    I_STATUS=''    #why these variables are here
    BT_STATUS=''
    print("SERVER_TYPE->",SERVER_TYPE)
    print("HOST->",HOST)
    print("PORT->",PORT)
    print("C_STATUS->",C_STATUS)
    print("PUBLISH_TOPIC->",PUBLISH_TOPIC)
    print("PUBFLAG->",PUBFLAG)
    print("N_STATUS->",N_STATUS)
    print("SCAN_TIME->",SCAN_TIME)
    print("LOGGINGFLAG->",LOGGINGFLAG)
    print("STORAGEFLAG->",STORAGEFLAG)

    #if STORAGEFLAG=='Active' and LOGGINGFLAG=='Active':
        #from gatewayapp.database import p1 as db

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
        if (prev_HOST!=HOST or prev_PORT!=PORT) and C_STATUS=='Active':
            s=1
            print("-"*20)
            print("Server setting")
            if chgEvent.isSet():
                chgEvent.clear()
            if connflag==True:
                client.loop_stop()
                client.disconnect()
            client = mqtt.Client()
            print("Connecting to cloud...")
            try:
                funInitilise(client,SERVER_TYPE,HOST,PORT)
                client.loop_start()
                chgEvent.set()
                print("-"*20)
                prev_HOST=HOST
                prev_PORT=PORT
                now=datetime.now()
                time_stamp=now.strftime("%m/%d/%Y, %H:%M:%S")
                client.publish(LOG_TOPIC, json.dumps({ "Timestamp" : time_stamp,"DeviceID":ID,"Source":"App","Log":{"Msg":"App main started and connected to cloud.","SERVER_TYPE":SERVER_TYPE,"HOST":HOST,"PORT":PORT,"C_STATUS":C_STATUS,"PUBLISH_TOPIC":PUBLISH_TOPIC,"PUBFLAG":PUBFLAG,"N_STATUS":N_STATUS,"SCAN_TIME":SCAN_TIME,"LOGGINGFLAG":LOGGINGFLAG,"STORAGEFLAG":STORAGEFLAG}}),0)
            except:
                print('could not connect to cloud! trying again...')
                time.sleep(1)
        #print("main loop")
        time.sleep(1)
    #-------------------------------------------------------------------------------------------------
#client.publish(jobstatustopic, json.dumps({ "status" : "SUCCEEDED"}),0)
#"SERVER_TYPE->":SERVER_TYPE,"HOST->":HOST,"PORT->":PORT,"C_STATUS->":C_STATUS,"PUBLISH_TOPIC->":PUBLISH_TOPIC,"PUBFLAG->":PUBFLAG,"N_STATUS->":N_STATUS,"SCAN_TIME->":SCAN_TIME,"LOGGINGFLAG->":LOGGINGFLAG,"STORAGEFLAG->":STORAGEFLAG
