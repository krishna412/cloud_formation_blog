'Update or create a stack given a name and template + params'
from __future__ import division, print_function, unicode_literals

from datetime import datetime
import logging
import json
import sys

import boto3
import botocore

cf = boto3.client('cloudformation')  # pylint: disable=C0103
log = logging.getLogger('deploy.cf.create_or_update')  # pylint: disable=C0103

def create_bucket():
    region = 'us-west-2'
    try:
        s3_client = boto3.client('s3', region_name = region)
        location = {'LocationConstraint': region}
        s3_client.create_bucket(Bucket = 'surya-lambda-code-store', CreateBucketConfiguration = location)
        
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            return True
        print (e)
        return False

def push_lambda_code():
    if create_bucket() == True:
        s3Resource = boto3.resource('s3')
        try: 
            s3Resource.meta.client.upload_file('lambda_functions/lambda.zip', 'surya-lambda-code-store', 'lambda.zip')
            s3Resource.meta.client.upload_file('lambda_functions/athena_lambda_function.zip', 'surya-lambda-code-store', 'athena_lambda_function.zip')
            return True
        except Exception as err:
            print(err)

def main(stack_name, template, parameters):
    'Update or create stack'

    template_data = _parse_template(template)
    parameter_data = _parse_parameters(parameters)

    params = {
        'StackName': stack_name,
        'TemplateBody': template_data,
        'Parameters': parameter_data,
        'Capabilities': ['CAPABILITY_IAM']
    }
    try:
        if _stack_exists(stack_name):
            print('Updating {}'.format(stack_name))
            stack_result = cf.update_stack(**params)
            waiter = cf.get_waiter('stack_update_complete')
        else:
            print('Creating {}'.format(stack_name))
            stack_result = cf.create_stack(**params)
            waiter = cf.get_waiter('stack_create_complete')
        print("...waiting for stack to be ready...")
        waiter.wait(StackName=stack_name)
    except botocore.exceptions.ClientError as ex:
        error_message = ex.response['Error']['Message']
        if error_message == 'No updates are to be performed.':
            print("No changes")
        else:
            raise
    else:
        print(json.dumps(
            cf.describe_stacks(StackName=stack_result['StackId']),
            indent=2,
            default=json_serial
        ))


def _parse_template(template):
    with open(template) as template_fileobj:
        template_data = template_fileobj.read()
    cf.validate_template(TemplateBody=template_data)
    return template_data


def _parse_parameters(parameters):
    with open(parameters) as parameter_fileobj:
        parameter_data = json.load(parameter_fileobj)
    return parameter_data


def _stack_exists(stack_name):
    stacks = cf.list_stacks()['StackSummaries']
    for stack in stacks:
        if stack['StackStatus'] == 'DELETE_COMPLETE':
            continue
        if stack_name == stack['StackName']:
            return True
    return False


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError("Type not serializable")


#if __name__ == '__main__':
def caller(a, b, c):
    print('inside caller')
    if push_lambda_code() == True:
        #main(*sys.argv[1:])
        main(a, b, c)
        return True