from flask import render_template, request, redirect, session, url_for  #necessary Imports
import subprocess   #module import for dealing with execution of console command
from gdmApp import app
from .database import p1 as db
import os
from .configHandler import ConfigHandler
confObject=ConfigHandler()



path='/var/opt/gateway/certUploads/'
ip=""
try:
    ip=os.popen('ip addr show eth1').read().split("inet ")[1].split("/")[0]
except:
    ip='Retrieving'

@app.route('/login',methods=['GET','POST'])   #route for handling login
def login():
    if request.method=="POST":
        if request.form.get('user')=='admin' and request.form.get('pas')=='admin':
            session['logedIn']='admin'
            return redirect('/')
        return render_template('login.html',msg='Wrong Credentials')
    return render_template('login.html')

@app.route('/logOut')    #route for handling logout
def logOut():
    if 'logedIn' in session:
        session.pop('logedIn')    #removing session
    return redirect(url_for('login'))

@app.route('/')
def home():
    if 'logedIn' in session:                #verifying user is logedIn or not
        node=confObject.getData("node")
        nodeData={'scanRate':node["SCAN_TIME"],'status':node["N_STATUS"]}
        cloud=confObject.getData("cloud")
        server=cloud["SERVER_TYPE"]
        serverType=''
        if server=='custom':
            serverType='Unsecured'
        else:
            serverType='Secured'
        cloudData={'server':server,'serverType':serverType,'hostAdd':cloud["HOST"],'port':cloud["PORT"],'status':cloud['C_STATUS'],'topic':cloud['publishTopic'],'pubFlag':cloud['PUBFLAG']}
        return render_template('home.html',nodeData=nodeData,cloudData=cloudData,deviceData=ip)
    return redirect(url_for('login'))

@app.route('/deviceConfig')
def deviceConfig():
    if 'logedIn' in session:
        return render_template('deviceConfig.html',deviceData=ip)
    return redirect(url_for('login'))

@app.route('/cloudConfig',methods=['GET','POST'])
def cloudConfig():
    if 'logedIn' in session:
        if request.method=="POST":     #need db integration for here
            if 'status' in request.form:
                confObject.updateData('cloud',{'C_STATUS':request.form['status']})
            server=request.form.get('server')
            if 'server' in request.form:
                di={'SERVER_TYPE':server,'HOST':request.form['hostAdd'],'PORT':request.form['port'],'PUBFLAG':'False'}
                confObject.updateData('cloud',di)
            if server=='aws':
                root=request.files['rootFile']                  #accessing the uploaded files
                pvtKey=request.files['pvtKey']
                iotCert=request.files['iotCert']
                root.save(path+'root.pem')        #saving the uploaded files
                pvtKey.save(path+'key.pem.key')
                iotCert.save(path+'cert.pem.crt')
        cloud=confObject.getData("cloud")
        server=cloud['SERVER_TYPE']
        serverType=''
        if server=='custom':
            serverType='Unsecured'
        else:
            serverType='Secured'
        cloudData={'server':server,'serverType':serverType,'hostAdd':cloud["HOST"],'port':cloud["PORT"],'status':cloud['C_STATUS'],'topic':cloud['publishTopic'],'pubFlag':cloud['PUBFLAG']}
        return render_template('cloudConfig.html',cloudData=cloudData)
    return redirect(url_for('login'))

@app.route('/nodeConfig',methods=['GET','POST'])
def nodeConfig():
    if 'logedIn' in session:
        if request.method=="POST":
            confObject.updateData('node',{'SCAN_TIME':request.form['scanRate'],'N_STATUS':request.form['status']})
        nodeData=confObject.getData('node')
        nodeData={'scanRate':nodeData['SCAN_TIME'],'status':nodeData['N_STATUS']}
        return render_template('nodeConfig.html',nodeData=nodeData)
    return redirect(url_for('login'))

@app.route('/netConfig')
def networkConfig():
    if 'logedIn' in session:
        return render_template('networkConfig.html')
    return redirect(url_for('login'))

@app.route('/debug')
def debug():
    if 'logedIn' in session:
        cmdKey=request.args.get('cmd')          #extracting the command key from the html form
        if cmdKey:
            cmd={'1':['hciconfig'],'2':['btmgmt','--index','0','info'],'3':['btmgmt','--index','0','find','-l'],'4':['systemctl','status','apache2'],'5':['systemctl','status','app']}
            if cmdKey in cmd:
                data=subprocess.Popen(cmd[cmdKey],stdout=subprocess.PIPE).communicate()[0]      #executing the command and getting the data into string format
                data=data.decode('utf-8')                                                       #decoding the binary the data into string
                data=data.split('\n')
                return render_template('debug.html',data=data)
            else:
                return render_template('debug.html',data=['Wrong/No command selected try again.'])
        return render_template('debug.html',data=None)
    return redirect(url_for('login'))

@app.route('/reports')
def reports():
    if 'logedIn' in session:
        return render_template('reports.html')
    return redirect(url_for('login'))

@app.route('/dataManager')
def dataManager():
    if 'logedIn' in session:
        data=db.getdata('HistoricalData')
        return render_template('dataManager.html',data=data,type='Historical Data')
    return redirect(url_for('login'))

@app.route('/dataManager/offData')
def offlineData():
    if 'logedIn' in session:
        data=db.getdata('OfflineData')
        return render_template('dataManager.html',data=data,type='Offline Data')
    return redirect(url_for('login'))
