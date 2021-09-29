from essentialImports import *
from  ConfigHandler import ConfigHandler
import time
import threading

def job(client,obj,msg):
    # This callback will only be called for messages with topics that match
    # $aws/things/Test_gateway/jobs/notify-next
    print("Job callback")
    print(str(msg.payload))
    jobconfig = json.loads(msg.payload.decode('utf-8'))
    t_job = threading.Thread(name='parse', target=parse,args=(jobconfig,client,mainBuffer,TOPIC))
    t_job.start()

def parse(jobconfig,client,mainBuffer,TOPIC):
    if 'execution' in jobconfig:
        jobid = jobconfig['execution']['jobId']
        cat = jobconfig['execution']['jobDocument']['category']
        operation = jobconfig['execution']['jobDocument']['operation']
        cmd=jobconfig['execution']['jobDocument'][cat]

        if cat=='cloud':
            value=cmd['value']
            task=cmd['task']
        #led_config=jobconfig['execution']['jobDocument']['led']

            if task=='publish_status' and value=='start':
                mainBuffer['dbCmnd'].append({'table':'Cloud','operation':'update','value':'True','column':'PUBFLAG','source':'job'})
                print("Publish Started")

            elif task=='publish_status' and value=='stop':
                mainBuffer['dbCmnd'].append({'table':'Cloud','operation':'update','value':'False','column':'PUBFLAG','source':'job'})
                print("Publish Stopped")

            if task=='publish_topic':
                mainBuffer['dbCmnd'].append({'table':'Cloud','operation':'update','value':value,'column':'TOPIC','source':'job'})
                print("Topic set",TOPIC)

        #if cat=='node':
        #if op=='read':
         #   rr=node.readp(j['MAC'],j['SERVICE'],j['CHAR'],j['CONFIG'])
        #publish rr
    #if op=='write':
     #   node.writep(j['MAC'],j['SERVICE'],j['CHAR'],j['CONFIG'])
        jobstatustopic = "$aws/things/Test_gateway/jobs/"+ jobid + "/update"
        #if operation=="publish" and cmd=="start":
        #    pubflag=True
        #elif operation=="publish" and cmd=="stop":
        #    pubflag=False
        #led config
        client.publish(jobstatustopic, json.dumps({ "status" : "SUCCEEDED"}),0)


def preq(led):
    while True:
        if not req.empty() and SCAN_STATUS=='Active':
            r=req.get()
            node.writep(r['MAC'],r['SERVICE'],r['CHAR'],r['CONFIG'])

def pconfig(mac,service,char,config):
    request={'MAC':mac,'SERVICE':service,'CHAR':char,'CONFIG':config}
    req.put(request,block=True,timeout=2)


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
                    publishData(client,dt,TOPIC,'True',mainBuffer,SERVER_TYPE)
                elif SERVER_TYPE == 'aws':
                    publishData(client,dt,TOPIC,PUBFLAG,mainBuffer,SERVER_TYPE)
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
    FLG=monEvent.wait()
    print("NODE STARTED")
    global SCAN_TIME
    while True:

        if len(mainBuffer['nodeCmnd'])!=0:

            job=mainBuffer['nodeCmnd'].popleft()
            operation=job['operation']
            #source=job['source']
            task=job['task']
            #value=job['value']
            #service=job['service']
            #char=job['char']
            #config=job['config']
            #mac=job['mac']



            # if task=='config':
                # if operation=='write':
                    # writeP(mac,service,char,config)

                # if operation=='read':
                    # p=readP(mac service,char)
                    # mainBuffer[source+'p']['value'].append(p)
        elif C_STATUS=='Active' and N_STATUS=='Active':
            payl=app_node(SCAN_TIME)
            if payl!=None:
                q.append(payl)
                print(len(q))
        time.sleep(1)

#def main():



if __name__=='__main__':
    mainBuffer={'cloud':deque([]),'monitor':deque([]),'dbCmnd':deque([]),'nodeCmnd':deque([])}
    confObject=ConfigHandler()
    confData=confObject.getDataForMain()

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

    #-------  THREAD Section ----------------------------------------------------------------------
    conEvent=threading.Event()
    monEvent=threading.Event()
    chgEvent=threading.Event()
    t_dbMaster=threading.Thread(name='dbMaster', target=dbMaster)
    t_dbMaster.start()
    t_nodeMaster=threading.Thread(name='nodeMaster', target=nodeMaster)
    t_nodeMaster.start()
    t_monitor = threading.Thread(name='monitor', target=monitor,args=(monEvent,conEvent,))
    t_monitor.start()
    t_cloud=threading.Thread(name='cloud', target=cloud)
    t_cloud.start()
    #-------------------------------------------------------------------------------------------------

    #-------  MAIN THREAD Section --------------------------------------------------------------------
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
            client.message_callback_add("$aws/things/Test_gateway/jobs/notify-next",job)
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
