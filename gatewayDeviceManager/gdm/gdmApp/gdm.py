from flask import render_template, request, redirect, session, url_for  #necessary Imports
import subprocess   #module import for dealing with execution of console command
from gdmApp import app
from .database import p1 as db
import os

path=(__file__).split('/')
path.pop()
path.pop()
path.pop()
path="/".join(path)
path=path+'/certUploads/'


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
        nodeData=db.getdata('Node')
        nodeData={'scanRate':nodeData[0][1],'status':nodeData[0][2]}
        cloudData=db.getdata('Cloud')
        server=cloudData[0][1]
        serverType=''
        if server=='custom':
            serverType='Unsecured'
        else:
            serverType='Secured'
        cloudData={'server':server,'serverType':serverType,'hostAdd':cloudData[0][2],'port':cloudData[0][3],'status':cloudData[0][4],'topic':cloudData[0][5],'pubFlag':cloudData[0][6]}
        return render_template('home.html',nodeData=nodeData,cloudData=cloudData)
    return redirect(url_for('login'))

@app.route('/deviceConfig')
def deviceConfig():
    if 'logedIn' in session:
        return render_template('deviceConfig.html')
    return redirect(url_for('login'))

@app.route('/cloudConfig',methods=['GET','POST'])
def cloudConfig():
    if 'logedIn' in session:
        if request.method=="POST":     #need db integration for here
            if 'status' in request.form:
                db.updatetable('Cloud','C_Status',request.form['status'])
            server=request.form.get('server')
            if 'server' in request.form:
                db.updatetable('Cloud','ServerType',server)
                db.updatetable('Cloud','Ip',request.form['hostAdd'])
                db.updatetable('Cloud','Port',request.form['port'])
                db.updatetable('Cloud','PUBFLAG','False')
            if server=='aws':
                root=request.files['rootFile']                  #accessing the uploaded files
                pvtKey=request.files['pvtKey']
                iotCert=request.files['iotCert']
                root.save(path+'root.pem')        #saving the uploaded files
                pvtKey.save(path+'key.pem.key')
                iotCert.save(path+'cert.pem.crt')
        cloudData=db.getdata('Cloud')
        server=cloudData[0][1]
        serverType=''
        if server=='custom':
            serverType='Unsecured'
        else:
            serverType='Secured'
        cloudData={'server':server,'serverType':serverType,'hostAdd':cloudData[0][2],'port':cloudData[0][3],'status':cloudData[0][4],'topic':cloudData[0][5],'pubFlag':cloudData[0][6]}
        return render_template('cloudConfig.html',cloudData=cloudData)
    return redirect(url_for('login'))

@app.route('/nodeConfig',methods=['GET','POST'])
def nodeConfig():
    if 'logedIn' in session:
        if request.method=="POST":
            db.updatetable('Node','ScaneRate',request.form['scanRate'])
            db.updatetable('Node','N_Status',request.form['status'])
        nodeData=db.getdata('Node')
        nodeData={'scanRate':nodeData[0][1],'status':nodeData[0][2]}
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
        os.system('lsblk -o mountpoint>withUsb.txt')
        data=subprocess.Popen(['diff','withoutUsb.txt','withUsb.txt'],stdout=subprocess.PIPE).communicate()[0]      #executing the command and getting the data into string format
        data=data.decode('utf-8')                                                       #decoding the binary the data into string
        data=data.split('\n')[1::2]
        if not data:
            data.append("No device connected")
        return render_template('dataManager.html',data=data,type='Historical Data')
    return redirect(url_for('login'))

@app.route('/dataManager/offData')
def offlineData():
    if 'logedIn' in session:
        data=db.getdata('OfflineData')
        return render_template('dataManager.html',data=data,type='Offline Data')
    return redirect(url_for('login'))
