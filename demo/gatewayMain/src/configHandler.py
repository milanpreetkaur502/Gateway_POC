import json

class ConfigHandler():

    def getDataForMain(self):
        dataDict={'ID':'','NAME':'','SERVER_TYPE':'','HOST':'','PORT':'','C_STATUS':'','N_STATUS':'','I_STATUS':'','SCAN_TIME':'','TOPIC':'','PUBFLAG':''}
        with open("/etc/gateway/config.conf",'r') as file:
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
        return dataDict

    def getData(self,name):
        with open(f"/etc/gateway/config.conf",'r') as file:
            data=json.load(file)
        return data[name]

    def updateData(self,name,keyValue):
        data={}
        with open(f"/etc/gateway/config.conf",'r') as file:
            data=json.load(file)
            dataa=data[name]
        with open(f"/etc/gateway/config.conf",'w') as file:
            dataa.update(keyValue)
            data.update({name:dataa})
            json.dump(data,file)
