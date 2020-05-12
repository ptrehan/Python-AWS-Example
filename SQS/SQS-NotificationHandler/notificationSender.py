"""
This file demostrates how clients can send various kinds of notification to SQS message queue.
Back end app that is pulling these notificatios off from the queue will process each notificaiton and
act according to rules
"""
import boto3
import time
import json
import logging
from botocore.exceptions import ClientError
logger = logging.getLogger(__name__)
class NotificationBuilder:
    def __init__ (self, type, data):
        self._type = type
        self._data = data
    def getData (self):
        return json.JSONEncoder ().encode ({'priority':self._type,'data':self._data})

def createSQSQueue (client, queue_name):
    try:
        
        queue = client.create_queue (QueueName=queue_name,
                                              Attributes={'MaximumMessageSize':'1024',
                                                          'MessageRetentionPeriod':'3600'})
    except ClientError as error:
        logger.exception ("Couldn't create SQS queue '%s'.",queue_name)
        raise error
    else:
        return queue

def notificationSender ():
    try:

        sqs_event_client = boto3.client ('sqs')
        queue_name = 'sqs-notification-wrapper'
        queue = createSQSQueue (sqs_event_client, queue_name)
    
        critical_msg = NotificationBuilder (1, "Critical message")
        print (critical_msg.getData ())
        sqs_event_client.send_message (QueueUrl=queue['QueueUrl'], MessageBody=critical_msg.getData ())

        normal_msg = NotificationBuilder (2, "Normal message")
        print (normal_msg.getData ())
        sqs_event_client.send_message (QueueUrl=queue['QueueUrl'], MessageBody=normal_msg.getData ())

    except ClientError as error:
        logger.exception("Couldn't send message '%s'.", msg.getData ())
        raise error



if __name__ == '__main__':
    notificationSender ()