import json
def parse(jobconfig,client,mainBuffer,TOPIC):
    if 'execution' in jobconfig:
        jobid = jobconfig['execution']['jobId']

    if jobconfig['execution']['jobdocument']['cloud']['enable']=='active':
        topic=jobconfig['execution']['jobdocument']['cloud']['topic']
        category=jobconfig['execution']['jobdocument']['cloud']['category']
        status=jobconfig['execution']['jobdocument']['cloud']['status']

        if task=='config':
            mainBuffer['dbCmnd'].append({'table':'Cloud','operation':'update','value':'True','column':'PUBFLAG','source':'job'})
            print("Publish Started")

        elif task=='publish_status' and value=='stop':
            mainBuffer['dbCmnd'].append({'table':'Cloud','operation':'update','value':'False','column':'PUBFLAG','source':'job'})
            print("Publish Stopped")

        if task=='publish_topic':
            mainBuffer['dbCmnd'].append({'table':'Cloud','operation':'update','value':value,'column':'TOPIC','source':'job'})
            print("Topic set",TOPIC)


        for i in topic:
            temptopic=topic[i]
            tempcategory=category[i]
            tempstatus=status[i]

    if jobconfig['execution']['jobdocument']['node']['enable']=='active':
        if jobconfig['execution']['jobdocument']['node']['operation']=='write':
            mac=jobconfig['execution']['jobdocument']['node']['mac']
            service=jobconfig['execution']['jobdocument']['node']['service']
            char=jobconfig['execution']['jobdocument']['node']['char']
            data=jobconfig['execution']['jobdocument']['node']['data']
            for i in mac:
                temptopic=topic[i]
                tempcategory=category[i]
                tempstatus=status[i]
                


        #if cat=='node':
        #if op=='read':
         #   rr=node.readp(j['MAC'],j['SERVICE'],j['CHAR'],j['CONFIG'])
        #publish rr
    #if op=='write':
     #   node.writep(j['MAC'],j['SERVICE'],j['CHAR'],j['CONFIG'])
        jobstatustopic = "$aws/things/Test_gateway/jobs/"+ jobid + "/update"
        #if operation=="publish" and cmd=="start":
        #    pubflag=True
        #elif operation=="publish" and cmd=="stop":
        #    pubflag=False
        #led config
        client.publish(jobstatustopic, json.dumps({ "status" : "SUCCEEDED"}),0)
