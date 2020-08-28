"""
-CloudWatch alert for System and Instance state monitoring. Publishes to the SNS topic labeled 'AWS_CloudWatch_to_Slack'
-This Lamba function, also named 'AWS_CloudWatch_to_Slack', subscribes to the previously mentioned SNS topic and receives the alert details
-The alert details are parsed into a json message that is delivered to Slack via webhook  
-The environment variable is configured in the AWS Lambda Dashboard for this function
"""

import json, os, requests

# environment variable webhook
WEBHOOK_URL=os.environ['WEBHOOK']
    
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
    
# parse alert body for message details we want to send to Slack.  Sends pertinent info to the 'send_alert_slace' function
def prepare_message(record):
    subject = record['Sns']['Subject']
    message = json.loads(record['Sns']['Message'])
    
    messageColor = ""
    
    if message['NewStateValue'] == "OK":
        message['NewStateValue'] = "OK  :white_check_mark:"
        messageColor = 'good'
    elif message['NewStateValue'] == "ALARM":
        message['NewStateValue'] = "ALARM  :fire:"
        messageColor = 'danger'
    
    body = {
    'text': subject,
    'attachments': [{
      'text': message['AlarmDescription'],
      'color' : messageColor,
      'fields': [{
        'title': '*Old State Value*',
        'value': message['OldStateValue'],
        'short': True,
      }, {
        'title': '*Alarm*',
        'value': message['AlarmName'],
        'short': True,
      }, {
        'title': '*Current State Value*',
        'value': message['NewStateValue'],
        'short': True,
      }, {
        'title': '*Region*',
        'value': message['Region'],
        'short': True,
      }],
    }],
    }
    return send_alert_slack(body)


# main handler
def lambda_handler(event, context):
    try:
        print("event received", json.dumps(event))

        # looping through events array of objects
        for single_event in event["Records"]:
            prepare_message(single_event)
    except Exception as e:
        raise Exception(e)
