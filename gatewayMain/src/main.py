from essentialImports import *

def job(client,obj,msg):
    # This callback will only be called for messages with topics that match
    # $aws/things/Test_gateway/jobs/notify-next
    print("Job callback")
    print(str(msg.payload))
    jobconfig = json.loads(msg.payload.decode('utf-8'))
    t_job = threading.Thread(name='parse', target=parse,args=(jobconfig,client,mainBuffer,TOPIC))
    t_job.start()

def monitor(monEvent,conEvent):
    print('MONITOR STARTED')
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
    while True:
        if len(mainBuffer['monitor'])!=0:
            dataa=mainBuffer['monitor'].popleft()
            ID=dataa['ID']
            NAME=dataa['NAME']
            HOST=dataa['HOST']
            PORT=dataa['PORT']
            C_STATUS=dataa['C_STATUS']
            N_STATUS=dataa['N_STATUS']
            I_STATUS=dataa['I_STATUS']
            SCAN_TIME=dataa['SCAN_TIME']
            SERVER_TYPE=dataa['SERVER_TYPE']
            TOPIC=dataa['TOPIC']
            PUBFLAG=dataa['PUBFLAG']
            monEvent.set()
        mainBuffer['dbCmnd'].append({'table':'','operation':'read','value':'','source':'monitor'})
        print("Cloud-",C_STATUS)
        print("Node-",N_STATUS)
        print("Scan-",SCAN_TIME)
        print("Host-",HOST)
        print("Pubflag-",PUBFLAG)
        print("Topic-",TOPIC)
        time.sleep(5)

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
        time.sleep(0.25)

def dbMaster():
    print("DB Started")
    while True:
        if len(mainBuffer['dbCmnd'])!=0:
            job=mainBuffer['dbCmnd'].popleft()
            source=job['source']
            table=job['table']
            value=job['value']

            if job['operation']=='read':
                if source=='monitor':
                    dataa=db.getdata('Device')
                    ID_=dataa[0][1]
                    NAME_=dataa[0][2]

                    dataa=db.getdata('Cloud')
                    SERVER_TYPE_=dataa[0][1]
                    HOST_=dataa[0][2]
                    PORT_=dataa[0][3]
                    C_STATUS_=dataa[0][4]
                    TOPIC_=dataa[0][5]
                    PUBFLAG_=dataa[0][6]

                    dataa=db.getdata('Node')
                    N_STATUS_=dataa[0][2]
                    I_STATUS_=dataa[0][3]
                    SCAN_TIME_=dataa[0][1]
                    payl={'ID':ID_,'NAME':NAME_,'SERVER_TYPE':SERVER_TYPE_,'HOST':HOST_,'PORT':PORT_,'C_STATUS':C_STATUS_,'N_STATUS':N_STATUS_,'I_STATUS':I_STATUS_,'SCAN_TIME':SCAN_TIME_,'TOPIC':TOPIC_,'PUBFLAG':PUBFLAG_}
                    mainBuffer[source].append(payl)

            if job['operation']=='write':
                if table=='HistoricalData':
                    db.putdata(table,value)
                if table=='OfflineData':
                    db.putdata(table,value)

            if job['operation']=='update':
                if table=='Cloud':
                    db.updatetable(table,job['column'],job['value'])

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

def main():

    mainBuffer={'cloud':deque([]),'monitor':deque([]),'dbCmnd':deque([]),'nodeCmnd':deque([])}

    #-------------------- GLOBAL VARIABLES  ------------------------------------------------------------
    ID=''
    NAME=''
    PROTOCOL=''
    HOST=''
    PORT=''
    N_STATUS=''
    C_STATUS=''
    I_STATUS=''
    BT_STATUS=''
    SCAN_TIME=''
    prev_HOST=''
    prev_PORT=''
    SERVER_TYPE=''
    TOPIC=''
    PUBFLAG=''
    q=deque([])
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


if __name__=='__main__':
    mainBuffer={'cloud':deque([]),'monitor':deque([]),'dbCmnd':deque([]),'nodeCmnd':deque([])}

    #-------------------- GLOBAL VARIABLES  ------------------------------------------------------------
    ID=''
    NAME=''
    PROTOCOL=''
    HOST=''
    PORT=''
    N_STATUS=''
    C_STATUS=''
    I_STATUS=''
    BT_STATUS=''
    SCAN_TIME=''
    prev_HOST=''
    prev_PORT=''
    SERVER_TYPE=''
    TOPIC=''
    PUBFLAG=''
    q=deque([])
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
