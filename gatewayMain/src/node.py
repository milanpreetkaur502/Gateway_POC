import json
from bluepy.btle import Scanner, DefaultDelegate , UUID, Peripheral
from multiprocessing import Process, Event
from time import sleep
import struct
import sys
from datetime import datetime
import subprocess

class BLEScanner:
    def __init__(self):
        self.scanner = Scanner()

        self.stop_event = Event()

    def startScan(self):

        self.stop_event.clear()

        self.process = Process(target=self.scan, args = ())
        self.process.start()
        return self

    def startP(self,task,mode,condition,mac,val,srv,ch):

        self.stop_event.clear()

        self.process = Process(target=self.peripheral, args = (task,mode,condition,mac,val,srv,ch))
        self.process.start()
        return self

    def scan(self):

        if self.stop_event.is_set():
            return

        self.devices = self.scanner.scan(2, passive=True)
        return self.devices
        '''
        for dev in self.devices:
            print("Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi))
            for (adtype, desc, value) in dev.getScanData():
                print("%s  %s = %s" % (adtype, desc, value))
        '''

    def peripheral(self,task,mode,condition,mac,val,srv,ch):
        for addr in mac:
            try:
                p = Peripheral(addr,"random")
                serv=p.getServiceByUUID(srv)
                char=serv.getCharacteristics(ch)[0]
                char.write(struct.pack('B',0x01))
                print("writing char:",addr)
                p.disconnect()
            except Exception as e:
                print(e)
                print("Exception:",addr)
            i+=1
            sleep(3)


    def stop(self):
        self.stop_event.set()

def hextodec(value):
    return -(value & 0x8000) | (value & 0x7fff) #coversion from signed hex to decimal


def writePeripheral(mac,service,char,config):
    led_service_uuid = UUID(service) #in string format
    led_char_uuid = UUID(char)

    p = Peripheral(mac, "random")
    led_srv=p.getServiceByUUID(led_service_uuid) # Service object for dev
    led_ch=led_srv.getCharacteristics(led_char_uuid)[0] # Charateristic object for dev
    if config=='Active':
        led_ch.write(struct.pack('B', 0x01))
    if config=='Inactive':
        led_ch.write(struct.pack('B', 0x00))
        p.disconnect()


def app_node(SCAN_TIME):

    #BLE Section
    bt=subprocess.check_output(['hciconfig'])#check for bluetooth status
    if b'UP' in bt:
        BT_STATUS='Active'
    else:
        BT_STATUS='Inactive'
        print('Node not connected')
    if BT_STATUS=='Active':
        #lescan=Scanner(0)
        #devices=lescan.scan(int(SCAN_TIME))
        c = Scanner()
        devices=c.scan(SCAN_TIME, passive=True)
        payload=[]
        devacc=0
        devtemp=0
        for dev in devices:
            dev_name=dev.getValueText(9)
            if dev_name=='Tag':
                man=dev.getValueText(255)#beacon manufacture data
                try:
                    #z=man[14:16] + man[12:14]
                    #y=man[10:12] + man[8:10]
                    #x=man[6:8] + man[4:6]
                    #x=hextodec(int(x, 16))*0.00245
                    #y=hextodec(int(y, 16))*0.00245
                    #z=hextodec(int(z, 16))*0.00245
                    type='Accelerometer'
                    now=datetime.now()
                    xx={'TYPE':'Beacon','MAC':dev.addr,'MACTYPE':dev.addrType,'RSSI':dev.rssi,'value':man,'sensorType':type,'Timestamp':int(datetime.timestamp(now))}
                    payload.append(xx)
                    devacc+=1
                except:
                    pass

            if dev_name=='TEMP':
                man=dev.getValueText(255)#beacon manufacture data
                try:
                    type='Temperature'
                    now=datetime.now()
                    xx={'TYPE':'Beacon','MAC':dev.addr,'MACTYPE':dev.addrType,'RSSI':dev.rssi,'value':man,'sensorType':type,'Timestamp':int(datetime.timestamp(now))}
                    payload.append(xx)
                    devtemp+=1
                except:
                    pass
        print('accelerometer device count ',devacc)
        print('temperature device count ',devtemp)
        SCAN_STATUS='Inactive'
        return payload


'''
payload.update({desc:value})
if not q.full() and C_STATUS=='Active':
q.put(payload,block=True,timeout=2)'''
