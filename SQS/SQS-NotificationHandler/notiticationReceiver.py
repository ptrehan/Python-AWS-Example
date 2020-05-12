
"""
This file demostrates how clients process messages as notification and perform different action based on
the notification. In this example we have two type of notifications:
priority 1, this will be recorded as well we will send notification to receipent.
priority 2, this will be only recorded in the db
"""
import boto3
import time
import json
import logging
import notificationSNS
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

def notificationReceiver ():
    try:

        sqs_event_client = boto3.client ('sqs')
        queue_name = 'sqs-notification-wrapper'
        queue = createSQSQueue (sqs_event_client, queue_name)

        topic_critical = notificationSNS.createTopic ('critical')
        print (topic_critical)
        notificationSNS.createCriticalSubscriber (topic_critical['TopicArn'])
        
        topic_normal = notificationSNS.createTopic ('normal')
        notificationSNS.createNormalSubscriber (topic_normal['TopicArn'])
        print (topic_normal)

        while (1):
            print ("Reading SQS Queue")
            responses = sqs_event_client.receive_message (QueueUrl=queue['QueueUrl'],
                                                          AttributeNames=['All'],
                                                          WaitTimeSeconds=20)
            if (len (responses) > 1):
                print (len(responses))
                for response in responses['Messages']:
                  #  print  (response ['MessageId'])
                  #  print  (response ['ReceiptHandle'])
                  #  print  (response ['Body'])
                    msg = response ['Body']
                    
                    body = json.loads (msg)
                    if (body ['priority'] == 1):
                        print ('Critical message received')
                        notificationSNS.publishSns (topic_critical['TopicArn'],body['data'])
                    else:
                        print ('Normal message received')
                        notificationSNS.publishSns (topic_normal['TopicArn'],body['data'])

                    
                    sqs_event_client.delete_message (QueueUrl=queue['QueueUrl'],ReceiptHandle=response ['ReceiptHandle'])
    except ClientError as error:
        logger.exception("Couldn't received message '%s'.", queue['QueueUrl'])
        raise error



if __name__ == '__main__':
    notificationReceiver ()