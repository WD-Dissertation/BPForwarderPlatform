from flask import Flask, jsonify, request, Response,json
import logging
from logging.handlers import SysLogHandler
import socket
from functools import reduce
import operator

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
    return 'BP Forwarder is running!'

#Configure BPM platforms to send webhooks to the '/webhook/' address.
@app.route('/webhook', methods=['POST'])
def webhook():

    #Webhooks use the 'Post' request, all other requests should be rejected.
    if request.method == 'POST':
        webhookPost = request.get_json()

        statusChange = {}

        #Cycle through possible BP Platforms the BP Forwarder is configured to receive webhooks from
        for bpPlat in BPM_Keys['bpms']:
            platform = platformCheck(webhookPost,BPM_Keys['bpms'][bpPlat])
            if bpPlat==platform:
                #Once BP platform identified, extract user-configured data from the webhook
				for bpkey in BPM_Keys[bpPlat]:
                    statusChange.update({bpkey: [reduce(operator.getitem, BPM_Keys[bpPlat][bpkey], webhookPost)]})

                #Output sanitised webhook data to remote syslog server.
                logger.info(statusChange)
                return 'Webhook received and forwarded'

        return 'Webhook received but BP Platform not registered in config file. Data not forwarded'
    else:
        return 'Request Method not supported', 405

def platformCheck(whData, subKeys):
    try:
        return reduce(operator.getitem, subKeys, whData)
    except(KeyError, TypeError):
        return None


if __name__ == '__main__':
    app.run()

