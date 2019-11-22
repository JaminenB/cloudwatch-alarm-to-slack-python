#Using Python 2.7 as Runtime in lambda function.
#file named 'main.py'
#Environmental function defined as 'WEBHOOK' for my Slack webhook.

import json, sys, os
from botocore.vendored import requests

# Environment Variable
WEBHOOK_URL=os.environ['WEBHOOK']

#Sends alert to slack using 'requests' module. JSON format
def send_alert_slack(message):
    try:
        r = requests.post(WEBHOOK_URL, json=message)
        r.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        raise Exception(errh)
    except requests.exceptions.ConnectionError as errc:
        raise Exception(errc)
    except requests.exceptions.Timeout as errt:
        raise Exception(errt)
    except requests.exceptions.RequestException as err:
        raise Exception(err)
    # print(requests)

#Prepares message by parsing out the wanted information from the SNS topic.
#Returns parsed information to the 'send_alert_slack' function.
def prepare_message(record):
    subject = record['Sns']['Subject']
    message = json.loads(record['Sns']['Message'])
    body = {
    'text': subject,
    'attachments': [{
      'text': message['NewStateReason'],
      'fields': [{
        'title': 'Time',
        'value': message['StateChangeTime'],
        'short': True,
      }, {
        'title': 'Alarm',
        'value': message['AlarmName'],
        'short': True,
      }, {
        'title': 'Account',
        'value': message['AWSAccountId'],
        'short': True,
      }, {
        'title': 'Region',
        'value': message['Region'],
        'short': True,
      }],
    }],
    }
    return send_alert_slack(body)

#Main handler that receives SNS topic - then calls prepare_message to parse the wanted information. 
def lambda_handler(event, context):
    try:
        print("event received", json.dumps(event))

        # looping through events array of objects
        for single_event in event["Records"]:
            prepare_message(single_event)
    except Exception as e:
        raise Exception(e)
