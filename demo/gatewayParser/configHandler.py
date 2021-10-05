import json

class ConfigHandler():

    def getDataForMain(self):
        dataDict={'ID':'','NAME':'','SERVER_TYPE':'','HOST':'','PORT':'','C_STATUS':'','N_STATUS':'','I_STATUS':'','SCAN_TIME':'','TOPIC':'','PUBFLAG':''}
        with open("/var/opt/gateway/device.conf",'r') as file:
            data=json.load(file)
            dataDict['ID']=data['SERIAL_ID']
            dataDict['NAME']=data['NAME']

        with open("/var/opt/gateway/cloud.conf",'r') as file:
            data=json.load(file)
            dataDict['SERVER_TYPE']=data['SERVER_TYPE']
            dataDict['HOST']=data['HOST']
            dataDict['PORT']=data['PORT']
            dataDict['C_STATUS']=data['C_STATUS']
            dataDict['TOPIC']=data['publishTopic']
            dataDict['PUBFLAG']=data['PUBFLAG']

        with open("/var/opt/gateway/node.conf",'r') as file:
            data=json.load(file)
            dataDict['N_STATUS']=data['N_STATUS']
            dataDict['SCAN_TIME']=data['SCAN_TIME']
        return dataDict

    def getData(self,name):
        with open(f"/var/opt/gateway/{name}.conf",'r') as file:
            data=json.load(file)
        return data

    def updateData(self,name,keyValue):
        data={}
        with open(f"/var/opt/gateway/{name}.conf",'r') as file:
            data=json.load(file)
        with open(f"/var/opt/gateway/{name}.conf",'w') as file:
            data.update(keyValue)
            json.dump(data,file)
