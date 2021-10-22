import json
import datetime

class ConfigHandler():

    def getDataForMain(self):
        dataDict={'ID':'','NAME':'','SERVER_TYPE':'','HOST':'','PORT':'','C_STATUS':'','N_STATUS':'','I_STATUS':'','SCAN_TIME':'','TOPIC':'','PUBFLAG':''}
        with open("/etc/gateway/config/gateway.conf",'r') as file:
            data=json.load(file)
            dataDict['ID']=data['device']['SERIAL_ID']
            dataDict['NAME']=data['device']['NAME']
            dataDict['SERVER_TYPE']=data['cloud']['SERVER_TYPE']
            dataDict['HOST']=data['cloud']['HOST']
            dataDict['PORT']=data['cloud']['PORT']
            dataDict['C_STATUS']=data['cloud']['C_STATUS']
            dataDict['TOPIC']=data['cloud']['publishTopic']
            dataDict['PUBFLAG']=data['cloud']['PUBFLAG']
            dataDict['N_STATUS']=data['node']['N_STATUS']
            dataDict['SCAN_TIME']=data['node']['SCAN_TIME']
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
        with open(f"/etc/gateway/network/network.conf",'a') as file:
            file.write("\n","Network change triggered at: ",ct)
