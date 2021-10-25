import json
import datetime

class ConfigHandler():

    def getDataForMain(self):
        dataDict={'ID':'','NAME':'','SERVER_TYPE':'','HOST':'','PORT':'','C_STATUS':'','N_STATUS':'','I_STATUS':'','SCAN_TIME':'','PUBLISH_TOPIC':'','PUBFLAG':'','JOB_TOPIC':'','OFFLINE_TOPIC':'','LOG_TOPIC':'','OTA_TOPIC':'','CATEGORY':'','COUNT':'','SCAN_RATE':'','NODE_TYPE':'','MAC_ADD':'','IP_ADD':'','VERSION':'','STATUS':'','LOCATION':'','GROUP':'','STORAGEFLAG':'','LOGGINGFLAG':''}
        with open("/etc/gateway/config/gateway.conf",'r') as file:
            data=json.load(file)

            dataDict['SERVER_TYPE']=data['cloud']['SERVER_TYPE']
            dataDict['HOST']=data['cloud']['HOST']
            dataDict['PORT']=data['cloud']['PORT']
            dataDict['C_STATUS']=data['cloud']['C_STATUS']
            dataDict['PUBLISH_TOPIC']=data['cloud']['PUBLISH_TOPIC']
            dataDict['JOB_TOPIC']=data['cloud']['JOB_TOPIC']
            dataDict['OFFLINE_TOPIC']=data['cloud']['OFFLINE_TOPIC']
            dataDict['LOG_TOPIC']=data['cloud']['LOG_TOPIC']
            dataDict['OTA_TOPIC']=data['cloud']['OTA_TOPIC']
            dataDict['PUBFLAG']=data['cloud']['PUBFLAG']

            dataDict['CATEGORY']=data['node']['CATEGORY']
            dataDict['COUNT']=data['node']['COUNT']
            dataDict['SCAN_RATE']=data['node']['SCAN_RATE']
            dataDict['N_STATUS']=data['node']['N_STATUS']
            dataDict['SCAN_TIME']=data['node']['SCAN_TIME']

            dataDict['NAME']=data['device']['NAME']
            dataDict['ID']=data['device']['SERIAL_ID']
            dataDict['NODE_TYPE']=data['device']['NODE_TYPE']
            dataDict['MAC_ADD']=data['device']['MAC_ADD']
            dataDict['IP_ADD']=data['device']['IP_ADD']
            dataDict['VERSION']=data['device']['VERSION']
            dataDict['STATUS']=data['device']['STATUS']
            dataDict['LOCATION']=data['device']['LOCATION']
            dataDict['GROUP']=data['device']['GROUP']
            dataDict['STORAGEFLAG']=data['device']['STORAGEFLAG']
            dataDict['LOGGINGFLAG']=data['device']['LOGGINGFLAG']
        return dataDict

    def getData(self,name):
        with open(f"/etc/gateway/config/gateway.conf",'r') as file:
            data=json.load(file)
        return data[name]

    def updateData(self,name,keyValue):
        data={}
        with open(f"/etc/gateway/config/gateway.conf",'r') as file:
            data=json.load(file)
            dataa=data[name]
        with open(f"/etc/gateway/config/gateway.conf",'w') as file:
            dataa.update(keyValue)
            data.update({name:dataa})
            json.dump(data,file,indent=4,separators=(',', ': '))

    def networkWatcher(self):
        ct=datetime.datetime.now()
        t=ct.strftime("%d/%m/%Y, %H:%M:%S")
        with open(f"/etc/gateway/network/network.conf",'a') as file:
            file.write("\n")
            file.write("Network change triggered at: ")
            file.write(t)

    def putdatacsv(self,data):
        with open("/media/flashdrive/output.csv","a") as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(data)
