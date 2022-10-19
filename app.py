"""
#BPForwarder Platform. This module receives a call from the Gunicorn WSGI
#with a webhook from a Business Process Management Platform, such as Jira.
#It parses the webhook and filters based on user-configured parameters.
#It forwards the filtered data via syslog.
"""
import logging
import socket
from functools import reduce
import operator
import re
from flask import Flask, request, json

app = Flask(__name__)

# Initialise Syslog Logger
logger = logging.getLogger("webhooklogger")
logger.setLevel(logging.INFO)
# Reverse SSH interface forwards port 2210 to remote syslog server.
handler = logging.handlers.SysLogHandler(
    address=("localhost", 2210), socktype=socket.SOCK_STREAM
)
logger.addHandler(handler)

# Import BP Forwarder Config file
with open("BPFconf.JSON", "r", encoding="utf8") as config_file:
    BPM_Keys = json.load(config_file)

#When navigating to the base website domain
@app.route("/")
def index():
"""
#Basic index page returned when website accessed through web browser.
#Confirms BP Forwarder is online.
"""
    return "BP Forwarder is running!", 200


# Note: Need to configure BPM platforms to send webhooks to the '/webhook/' subaddress.
@app.route("/webhook", methods=["POST"])
def webhook():
"""
# Webhook parser
# Webhooks use the 'Post' request, all other requests should be rejected.
"""
    if request.method == "POST":
        webhook_post = request.get_json()

        # Initialise dictionary to be forwarded as syslog
        status_change = dict()

        # Cycle through the candidate BP Platforms the BP Forwarder Configuration File
        #is configured to receive webhooks from (e.g. Jira, Backlog, Monday.com etc)
        for bp_plat in BPM_Keys["bpmsIdentPath"]:
            bp_id = data_check(webhook_post, BPM_Keys["bpmsIdentPath"][bp_plat])

            if BPM_Keys["bpmsIdentMapping"][bp_plat] == bp_id:
                # Once BP platform identified, extract user-configured BP data from the webhook
                status_change.update({"BPM_Platform": [bp_plat]})
                for bpkey in BPM_Keys[bp_plat]:
                    status_change.update(
                        {bpkey: data_sanitise(data_check(webhook_post, BPM_Keys[bp_plat][bpkey]))}
                    )

                # Output sanitised webhook data to remote syslog server.
                logger.info(status_change)
                # Proactively delete raw webhook data.
                del webhook_post
                del status_change
                return "Webhook received and forwarded", 200

        # Respond to 'challenge' required by some BPM Platforms, e.g. Monday.com
        if "challenge" in webhook_post.keys():
            return webhook_post, 200
        
        # Proactively delete raw webhook data.
        del webhook_post
        return (
            "Webhook received but BP Platform not registered in config file. Data not forwarded",
            200,
        )

    return "Request Method not supported", 405


def data_check(wh_data, sub_keys):
"""
#Function to search dictionary, incl. sub keys, according to specified key path
"""
    try:
        # search for BP Platform identifier key within the received webhook
        data = [reduce(operator.getitem, sub_keys, wh_data)]
        # Proactively delete raw webhook data.
        del wh_data
        return data
    except (KeyError, TypeError):
        # If BP Platform identifier key not found, return 'None'
        return None
    
def data_sanitise(data)
"""
#Sanitise data to remove excessive length and
#dangerous characters before returning
"""
    if data is not None:
        data = ([data[0][:60] + ".."]) if len(data[0]) > 60 else data
        # Keep +,:,-,' ', for date/time strings
        data = [re.sub(r"\W+:- ", " ", data[0])]
    return data


if __name__ == "__main__":
    app.run()
                
