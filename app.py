from flask import Flask, jsonify, request, Response,json
import logging
from logging.handlers import SysLogHandler
import socket
from functools import reduce
import operator
import re

app = Flask(__name__)

#Initialise Syslog Logger
logger = logging.getLogger("webhooklogger")
logger.setLevel(logging.INFO)
#Reverse SSH interface forwards port 2210 to remote syslog server.
handler = logging.handlers.SysLogHandler(address=("localhost",2210), socktype=socket.SOCK_STREAM)
logger.addHandler(handler)

#Import BP Forwarder Config file
with open('BPFconf.JSON', "r") as config_file:
    BPM_Keys = json.load(config_file)

#Basic index page returned when website accessed through web browser. Confirms BP Forwarder is online.
@app.route('/')
def index():
    return 'BP Forwarder is running!', 200

#Webhook parser
#Note: Need to configure BPM platforms to send webhooks to the '/webhook/' subaddress.
@app.route('/webhook', methods=['POST'])
def webhook():

    #Webhooks use the 'Post' request, all other requests should be rejected.
    if request.method == 'POST':
        webhookPost = request.get_json()

        #Initialise dictionary to be forwarded as syslog
        statusChange = {}

        #Cycle through the candidate BP Platforms the BP Forwarder Configuration File is configured to receive webhooks from (e.g. Jira, Backlog, Monday.com etc)
        for bpPlat in BPM_Keys['bpmsIdentPath']:
            bpID = dataCheck(webhookPost,BPM_Keys['bpmsIdentPath'][bpPlat])

            if BPM_Keys['bpmsIdentMapping'][bpPlat]==bpID:
                #Once BP platform identified, extract user-configured BP data from the webhook
                statusChange.update({"BPM_Platform": [bpPlat]})
                for bpkey in BPM_Keys[bpPlat]:
                    statusChange.update({bpkey: dataCheck(webhookPost,BPM_Keys[bpPlat][bpkey])})

                #Output sanitised webhook data to remote syslog server.
                logger.info(statusChange)
				return 'Webhook received and forwarded', 200
                
        #Respond to 'challenge' required by some BPM Platforms, e.g. Monday.com
        if 'challenge' in webhookPost.keys():
            return webhookPost, 200

        return 'Webhook received but BP Platform not registered in config file. Data not forwarded', 200
    else:
        return 'Request Method not supported', 405

def dataCheck(whData, subKeys):
    try:
        #search for BP Platform identifier key within the received webhook
        data = reduce(operator.getitem, subKeys, whData)
        #if found, sanitise associated data to remove excessive length and dangerous characters before returning
        data = (data[:40] + '..') if len(data) > 40 else data
        #Keep +,:,-,' ', for date/time strings
        data = re.sub('\W+:- ',' ',data)
        return [data]
    except(KeyError, TypeError):
        #If BP Platform identifier key not found, return 'None'
        return None


if __name__ == '__main__':
    app.run()


