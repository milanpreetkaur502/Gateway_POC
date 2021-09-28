# from essentialImports import *
from configHandler import ConfigHandler
import time
import threading

def cloud(client,que,C_STATUS,N_STATUS,SERVER_TYPE,TOPIC,PUBFLAG):
    print("CLOUD Started")
    while True:
        print('Hii from cloud')
        # if len(que)!=0 and C_STATUS=='Active' and N_STATUS=='Active':#and I_STATUS=='Active':
        #     d = que.popleft()
        #     for dev in d:
        #         now=datetime.now()
        #         dt = {'t_stmp' : int(datetime.timestamp(now)),
        #             't_utc' : now.strftime("%d/%m/%Y, %H:%M:%S"),
        #             'x' : dev['Accelerometer(x)'],
        #             'y' : dev['Accelerometer(y)'],
        #             'z' : dev['Accelerometer(z)'],
        #             'MAC' : dev['MAC'],
        #             'MACTYPE' : dev['MACTYPE'],
        #             'RSSI' : dev['RSSI']
        #             }

        #         if SERVER_TYPE == 'custom':
        #             publishData(client,dt,TOPIC,'True',SERVER_TYPE)
        #         elif SERVER_TYPE == 'aws':
        #             publishData(client,dt,TOPIC,PUBFLAG,SERVER_TYPE)
        time.sleep(3)

def nodeMaster(que,C_STATUS,N_STATUS,SCAN_TIME):
    print("NODE STARTED")
    while True:
        print("HII from node")
        # if C_STATUS=='Active' and N_STATUS=='Active':
        #     payl=app_node(SCAN_TIME)
        #     if payl!=None:
        #         que.append(payl)
        time.sleep(3)


if __name__=='__main__':

    confObject=ConfigHandler()
    confData=confObject.getDataForMain()
    que=[]

    #-------------------- GETTING DATA INTO VARIABLES FROM CONF FILES ---------------------------------
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
    #-------------------------------------------------------------------------------------------------


    #-------  CREATING MQTT CLIENT AND ESTABLISHING CONNECTION ----------------------------------------
    if SERVER_TYPE!='Unknown':
        print("Connecting to cloud...")
        # client = mqtt.Client()
        # funInitilise(client,SERVER_TYPE,HOST,PORT)
        # client.loop_start()
    else:
        print("Please do cloud configuration")
    #-------------------------------------------------------------------------------------------------

    #-------  THREAD Section ----------------------------------------------------------------------
    t_nodeMaster=threading.Thread(name='nodeMaster', target=nodeMaster,args=(que,C_STATUS,N_STATUS,SCAN_TIME))
    t_nodeMaster.start()
    t_cloud=threading.Thread(name='cloud', target=cloud,args=('',que,C_STATUS,N_STATUS,SERVER_TYPE,TOPIC,PUBFLAG))
    t_cloud.start()
    #-------------------------------------------------------------------------------------------------




