'''
This is a sample Lambda function that sends an SMS on click of a
button. It needs one permission sns:Publish. The following policy
allows SNS publish to SMS but not topics or endpoints.
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "sns:Publish"
            ],
            "Resource": [
                "*"
            ]
        },
        {
            "Effect": "Deny",
            "Action": [
                "sns:Publish"
            ],
            "Resource": [
                "arn:aws:sns:*:*:*"
            ]
        }
    ]
}

The following JSON template shows what is sent as the payload:
{
    "serialNumber": "GXXXXXXXXXXXXXXXXX",
    "batteryVoltage": "xxmV",
    "clickType": "SINGLE" | "DOUBLE" | "LONG"
}

A "LONG" clickType is sent if the first press lasts longer than 1.5 seconds.
"SINGLE" and "DOUBLE" clickType payloads are sent for short clicks.

For more documentation, follow the link below.
http://docs.aws.amazon.com/iot/latest/developerguide/iot-lambda-rule.html

To send a POST request to DynamoDB, use this format:
{
  "pageId":   "example-page-id",
  "userName": "ExampleUserName",
  "message":  "This is an example comment to be added."
}
'''

from __future__ import print_function

import boto3
import json
import logging
#import requests

jasonsPhoneNumber = '14078646891'
spencersPhoneNumber = '15022951782'

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sns = boto3.client('sns')
phone_number = spencersPhoneNumber

def lambda_handler(event, context):
    #sends SMS message
    logger.info('Received event: ' + json.dumps(event))
    message = 'Hi, this is Spencer\'s button. Have a nice day!'
    sns.publish(PhoneNumber=phone_number, Message=message)
    logger.info('SMS has been sent to ' + phone_number)

    #logs message details in DynamoDB table
    #dynamodb = boto3.client('dynamodb')
    #Item={'commentId':{'S':'Banana'},'message':{'S':'Banana'},'pageId':{'S':'Banana'},'userName':{'S':'Banana'}
    #dynamodb.put_item(TableName=Comments, Item)

    '''
    Attempting to make a POST request
    url = 'https://gti1r35si8.execute-api.us-east-1.amazonaws.com/test/comments'
    logger.info('url has been defined')
    payload = {'pageId':   'example-page-id2', 'userName': 'ExampleUserName2', 'message':  '2This is an example comment to be added.'}
    logger.info('payload has been defined')
    r = requests.post(url, data=json.dumps(payload))
    logger.info('request has been sent')
    '''
