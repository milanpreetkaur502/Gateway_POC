import sqlite3
import time

#conn = sqlite3.connect('/home/lab/gateway/Gateway_POC/mydatabasenew.db',check_same_thread=False)

class tables():

    def createTable(self,tablename, val):
        self.conn.execute('create table if not exists ' + tablename + val)
        self.conn.commit()
        print("table created")

    def __init__(self):
        self.conn = sqlite3.connect('/home/lab/gateway/Gateway_POC/demo/gatewayMain/src/mydatabasenew.db',check_same_thread=False)
        # self.conn = sqlite3.connect('/home/attu/Desktop/mydatabasenew.db',check_same_thread=False)
        try:
            self.conn.execute('select * from Cloud')
        except:
            self.calltable()
            self.callputdata()

    def calltable(self):
        val1 = (' (Key  int ,Id varchar(20) , Name varchar(20) , IPv4 varchar(20) , Interface varchar(20) , Status varchar(20)) ')
        val2 = (' ( key int ,ServerType varchar(20) ,Ip varchar(100) , Port varchar(20) , C_Status varchar(20) , TOPIC varchar(40), PUBFLAG varchar(20)) ')
        val3 = (' (key int ,ScaneRate varchar(20)  , N_Status varchar(20) , I_Status varchar(20) ) ')
        val4 = ('(Id int , MacAdd varchar(20) , rssi varchar(20) , value varchar(20) , sensorType varchar(20) , date varchar(20) )')
        val5 = ('(Id int , MacAdd varchar(20) , rssi varchar(20) , value varchar(20) , sensorType varchar(20) , date varchar(20))')

        self.createTable('Device', val1)
        self.createTable('Cloud', val2)
        self.createTable('Node', val3)
        self.createTable('HistoricalData', val4)
        self.createTable('OfflineData', val5)

    def getdata(self,tableselect):

        try:
            data=self.conn.execute('select * from ' + tableselect)
            data=data.fetchall()
            return data

        except:
            time.sleep(2)
            return self.getdata(tableselect)

    def getdatadate(tableselect,s,p):
        d=self.conn.execute('select * from ' + tableselect + 'where date > = '+ s + 'and date < =' + p)
        d=d.fetchall()
        return d

    def configdataread(self):
        data = self.getdata('Device')
        print(data)
        data = self.getdata('Cloud')
        print(data)
        data = self.getdata('Node')
        print(data)


    def HistoricalDataread(self):
        data = self.getdatadate('HistoricalData')
        print(data)


    def offlinedataread(self):
        data = self.getdata('OfflineData')
        print(data)


    def callgetdata(self):
        self.getdata('Device')
        self.getdata('Cloud')
        self.getdata('Node')
        self.getdata('HistoricalData')
        print(self.getdata('OfflineData'))


    def putdata(self,tablevalue, data):
        try:
            query = f'insert into {tablevalue} values {data}'
            self.conn.execute(query)
            self.conn.commit()
        except Exception as e:
            time.sleep(2)
            print('cannot write to db')
            print(e)
            #elf.putdata(tablevalue,data)


    def callputdata(self):
        self.putdata('Device', ('1', '1100110011', 'Test Device', '172.23.0.26', 'ETHERNET', 'Inactive'))
        self.putdata('Cloud', ('1','custom', '0.0.0.0', '8883', 'Inactive','beacon','False'))
        self.putdata('Node', ('1' ,'3', 'Inactive', 'Inactive'))
        #self.putdata('HistoricalData', ('1', '1100110011', 'Test Device', '172.23.0.26', 'ETHERNET', '20' , '20' , '20' ,'2021-09-03'))
        #self.putdata('OfflineData', ('1', '1100110011', 'Test Device', '172.23.0.26', 'ETHERNET', '20' , '20' , '20' ,'2021-09-03'))


    def deletetable(self,tablename):
        d = 'delete from ' + tablename
        print(d)
        self.conn.execute(d)


    def updatetable(self,tablename, c, v):
        #print('hmmmmmmm')
        try:
            p = f"update {tablename} set {c} = '{v}' where Key = 1"
            #print('hmmm')
            self.conn.execute(p)
            self.conn.commit()
        except Exception as e:
            print(e)
            #time.sleep(2)
            #self.updatetable(tablename,c,v)

    def putdatabeacon(self,tablevalue, data):
        try:
            query = f'insert into {tablevalue} (MacAdd , rssi  , value , sensorType ,date) values {data}'
            print(query)
            self.conn.execute(query)
            self.conn.commit()
        except Exception as e:
            time.sleep(2)
            print(e)
            #self.putdatabeacon(tablevalue,data)
    def close(self):
        self.conn.close()

p1=tables()
#print(p1.getdata('Node'))
#p1.calltable()

#p1.callgetdata()
#p1.configdataread()
#p1.HistoricalDataread()
#p1.offlinedataread()
#p1.callputdata()
#p1.configdataread()
#p1.close()
#p1.deletetable()
