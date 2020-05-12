
"""
This file implements SNS publisher and subscriber. It creates two topics "critical" and "normal".
If message is pused to "normal" topic than it is logged in S3 logs through lamda subscriber.
If message is pused to "critical" topic than it is logged in log and also email notification is sent.
"""
import boto3
import logging
import json
import time
import notificationLambda

sns_client = boto3.client ('sns')

def createTopic (topic):
    return sns_client.create_topic(Name=topic)

def createCriticalSubscriber (topic_arn):
    value = input("Do you want to send critical notfication to email {Y/y}:\n")
    if (value.upper () == 'Y'):
        email_addr = input ("Please enter your email:\n")
        print ("You entered:" + email_addr)
        createEmailSubscriber (topic_arn,'email',email_addr)
    createLambdaSubscriber (topic_arn)

def createNormalSubscriber (topic_arn):
    createLambdaSubscriber (topic_arn)

def createEmailSubscriber (topic_arn, protocol, endpoint):
    existing_sub = sns_client.list_subscriptions_by_topic (TopicArn=topic_arn)
    for sub in existing_sub['Subscriptions']:
        if (sub['Protocol'] == protocol and sub['Endpoint'] == endpoint):
            return
    sns_client.subscribe (TopicArn=topic_arn, Protocol=protocol,Endpoint=endpoint)

def createLambdaSubscriber (topic_arn):
    protocol='lambda'
    existing_sub = sns_client.list_subscriptions_by_topic (TopicArn=topic_arn)
    id = 'sns'
    lambda_arn = notificationLambda.createLambaFunction ("sns_lambda_func","lambdaFunction.py","lambda_handler","sns_iam_role",'lambda:InvokeFunction','sns.amazonaws.com',topic_arn,id)
    
    notificationLambda.addPermissionLamdaFunction ("sns_lambda_func",'lambda:InvokeFunction',
                                                   'sns.amazonaws.com',topic_arn,id )
    for sub in existing_sub['Subscriptions']:
        if (sub['Protocol'] == protocol and sub['Endpoint']==lambda_arn):
            return
    result = sns_client.subscribe (TopicArn=topic_arn, Protocol=protocol, Endpoint=lambda_arn) 
    return result

def publishSns (topic_arn, data):
    sns_client.publish (TopicArn=topic_arn,Message=data,Subject='Attention please')