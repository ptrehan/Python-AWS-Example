import boto3
import logging
import json
from botocore.exceptions import ClientError

iam_client = boto3.client ('iam')

def getIAMRoleArn (iam_role_name):
    try:
        result = iam_client.get_role (RoleName=iam_role_name)
    except ClientError as e:
        logging.error (e)
        return

    return result ['Role']['Arn']

def isIAMRoleExist (iam_role_name):
    if (getIAMRoleArn (iam_role_name) is None):
        return False
    return True


def createIAMRole (rolename):
    status = isIAMRoleExist (rolename)
    if (status == True):
        lamba_role_arn = getIAMRoleArn (rolename)
        role_exist = True
    else:
        role_exist = False

    lambda_assume_role = {
        'Version': '2012-10-17',
        'Statement': [
            {
                'Sid': '',
                'Effect': 'Allow',
                'Principal': {
                    'Service': 'lambda.amazonaws.com'
                },
                'Action': 'sts:AssumeRole'
            }
        ]
    }
    if (not role_exist):
        try:
            result = iam_client.create_role (RoleName=rolename, AssumeRolePolicyDocument = json.dumps (lambda_assume_role))
        except ClientError as e:
            logging.error (e)
            return
        lambda_role_arn = result['Role']['Arn']

    lambda_policy_arn = 'arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
    try:
        iam_client.attach_role_policy(RoleName=rolename,
                                      PolicyArn=lambda_policy_arn)
    except ClientError as e:
        logging.error(e)
        return None
    return lamba_role_arn
