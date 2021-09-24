import json
def parse(jobconfig,client,mainBuffer,TOPIC):
    if 'execution' in jobconfig:
        jobid = jobconfig['execution']['jobId']
        cat = jobconfig['execution']['jobDocument']['category']
        operation = jobconfig['execution']['jobDocument']['operation']
        cmd=jobconfig['execution']['jobDocument'][cat]

        if cat=='cloud':
            value=cmd['value']
            task=cmd['task']
        #led_config=jobconfig['execution']['jobDocument']['led']

            if task=='publish_status' and value=='start':
                mainBuffer['dbCmnd'].append({'table':'Cloud','operation':'update','value':'True','column':'PUBFLAG','source':'job'})
                print("Publish Started")

            elif task=='publish_status' and value=='stop':
                mainBuffer['dbCmnd'].append({'table':'Cloud','operation':'update','value':'False','column':'PUBFLAG','source':'job'})
                print("Publish Stopped")

            if task=='publish_topic':
                mainBuffer['dbCmnd'].append({'table':'Cloud','operation':'update','value':value,'column':'TOPIC','source':'job'})
                print("Topic set",TOPIC)

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
