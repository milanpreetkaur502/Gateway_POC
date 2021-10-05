##BLE Observer/Central, connects to all Nordic blinky devices 
#ARV
#Tested on iMX6

from bluepy.btle import Scanner, DefaultDelegate , UUID, Peripheral
from time import sleep
import struct
import sys


# ScanDelegate custom class on Default delegate base class obj
#Handles notification events while  LE scanning

def node_peripheral(task,mode,condition,mac,val,srv,ch):
    if task == "ch_write":
        print("Write Mode")
        if mode == "all":
            pass
        elif mode == "multi":
            i=0
            print("Multi device")
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
        return
                
    
    


'''scanner = Scanner(0)
devices = scanner.scan(3)
dev_addr=[]   # store MAC
              
for dev in devices:
    dev_name=dev.getValueText(9) # extracting adv packet with type id 9 for local name field
    if dev_name=='Tag':
        dev_addr.append(dev.addr)

print(dev_addr)
print("Device Count-",len(dev_addr))

print("Value-",val)'''


##Reference Service and Charatertistic ID variable for led control
led_service_uuid = UUID("f3641400-00b0-4240-ba50-05ca45bf8abc")
led_char_uuid = UUID("f3641401-00b0-4240-ba50-05ca45bf8abc")
dev_addr=["c3:83:0c:de:ae:07","d1:f1:de:05:90:f5","cb:f2:72:82:5a:b6"]
val=[0x01]*len(dev_addr)

#Creating peripheral devices (Need to make it dynamic)

node_peripheral("ch_write","multi","Null",dev_addr,val,led_service_uuid,led_char_uuid)


print("DONE")


