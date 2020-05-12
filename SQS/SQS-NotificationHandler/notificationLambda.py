
import boto3
import logging
import os
import zipfile
import zlib
import notificationIAM
import json
from botocore.exceptions import ClientError

lambda_client = boto3.client ('lambda')
def deploy_lambda_function(name, iam_role, handler, deployment_package,action, principal, sourceArn, id):


    try:
        function_list = lambda_client.list_functions ()
        for f in function_list['Functions']:
            if (f['FunctionName']==name) and (f['Runtime']=='python3.8'):
                return f
        with open(deployment_package, mode='rb') as pkg:
            deploy_pkg = pkg.read()
        result = lambda_client.create_function (FunctionName=name,
                                                Runtime='python3.8',
                                                Role=iam_role,
                                                Handler=handler,
                                                Code={'ZipFile':deploy_pkg})
        lambda_client.add_permission (FunctionName=name,
                                  Action=action,
                                  Principal=principal,
                                  SourceArn=sourceArn,
                                  StatementId=id)
    except ClientError as e:
        logging.error (e)
        return None

    return result


def createLambaFunction (function_name, srcfile, handler_name, iam_role_name, action, principal, sourceArn, id):


    filename, _ = os.path.splitext(srcfile)

    deployment_package = f'{filename}.zip'
    with zipfile.ZipFile(deployment_package, mode='w',
                         compression=zipfile.ZIP_DEFLATED,
                         compresslevel=zlib.Z_DEFAULT_COMPRESSION) as deploy_pkg:
        try:
            deploy_pkg.write(srcfile)
        except Exception as e:
            logging.error(e)
            return None

    iam_role_arn = notificationIAM.createIAMRole (iam_role_name)
    if iam_role_arn is None:
        return None

    microservice = deploy_lambda_function(function_name, iam_role_arn,
                                          f'{filename}.{handler_name}',
                                          deployment_package, action, principal, sourceArn, id)
    if microservice is None:
        return None
    lambda_arn = microservice['FunctionArn']

    logging.info(f'Created Lambda function: {function_name}')
    logging.info(f'ARN: {lambda_arn}')
    return lambda_arn

def addPermissionLamdaFunction (functionName, action, principal, sourceArn, id):
    res = lambda_client.get_policy (FunctionName=functionName)
    
    r = json.loads (res['Policy'])
    for st in r['Statement']:
        print (st ['Principal'])
        arn = st ['Condition']['ArnLike']['AWS:SourceArn']
        print (arn)
        if (st ['Principal']['Service'] == principal) and (st ['Action'] == action) and (arn == sourceArn):
            return
    id = id + str (len (r['Statement']))

    response = lambda_client.add_permission (FunctionName=functionName,
                                  Action=action,
                                  Principal=principal,
                                  SourceArn=sourceArn,
                                  StatementId=id)
    print (response)
 