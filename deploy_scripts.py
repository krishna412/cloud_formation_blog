from datetime import datetime
import logging
import json
import sys
import boto3
import botocore

cf_package = boto3.client('cloudformation')

'''
    Module to create S3 bucket which stores lambda functions.
    @Author: Suryadeep
    @Version: 1.0
'''
def create_bucket():
    print('Creating bucket')
    region = 'us-west-2'
    try:
        s3_client = boto3.client('s3', region_name = region)
        location = {'LocationConstraint': region}
        s3_client.create_bucket(Bucket = 'surya-lambda-code-store', 
                                CreateBucketConfiguration = location)
        
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            return True
        print (e)
        return False
    # Return True when created.
    return True

'''
    Module to push lambda codes into the bucket.
    @Author: Suryadeep
    @Version: 1.0
'''
def push_lambda_code():
    print('pushing lambda codes')
    file_1_src = 'lambda_functions/lambda.zip'
    file_2_src = 'lambda_functions/athena_lambda_function.zip'

    if create_bucket() == True:
        s3Resource = boto3.resource('s3')
        try: 
            s3Resource.meta.client.upload_file(file_1_src, 
                                                'surya-lambda-code-store', 
                                                'lambda.zip')

            s3Resource.meta.client.upload_file(file_2_src, 
                                                'surya-lambda-code-store', 
                                                'athena_lambda_function.zip')
            return True
        except Exception as err:
            print(err)


# Module to check if the template is valid.
def check_temp_validity(template):
    with open(template) as t_obj:
        t_data = t_obj.read()
    cf_package.validate_template(TemplateBody = t_data)
    return t_data

# Module to check if params are valid.
def check_params_validity(parameters):
    with open(parameters) as p_obj:
        p_data = json.load(p_obj)
    return p_data

# Check if a stack exists with the
# current name.
def check_stack_status(stack_name):
    stacks = cf_package.list_stacks()['StackSummaries']
    for stack in stacks:
        if stack['StackStatus'] == 'DELETE_COMPLETE':
            continue
        if stack_name == stack['StackName']:
            print('stack')
            return True
    return False

# Parse the arguments in the
# expected format.
def create_args(stack_name, template_vals, param_vals):
    valid_temp = check_temp_validity(template_vals)
    valid_param = check_params_validity(param_vals)
    arguments = {
        'StackName': stack_name,
        'TemplateBody': valid_temp,
        'Parameters': valid_param,
        'Capabilities': ['CAPABILITY_IAM']
    }
    return arguments

# Module to initiate stack creation.
def init_stack(pass_args):
    try:
        # If the stack already exists update.
        if check_stack_status(pass_args['StackName']):
            print('Stack already exists')
            print('Updating stack.')
            stack_result = cf_package.update_stack(**pass_args)
            waiter = cf_package.get_waiter('stack_update_complete')
        
        else:
            # Create stack if does not exist.
            print('Creating ',pass_args['StackName'])
            stack_result = cf_package.create_stack(**pass_args)
            waiter = cf_package.get_waiter('stack_create_complete')
            print('Preparing the stack')
            waiter.wait(StackName = pass_args['StackName'])
            print('stack created')

    except botocore.exceptions.ClientError as ex:
        # Check for exception when no change
        # required.
        if ex.response['Error']['Message'] == 'No updates are to be performed.':
            print("No modification noted")
        else:
            print(ex)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Please enter the stack name in the following format-')
        print('python <filename.py> <StackNameme>')

    else:
        if push_lambda_code() == True:
            stk = sys.argv[1]
            template_loc = 'src/cf_scripts.json'
            param_loc = 'src/params.json'
            args = create_args(stk, template_loc, param_loc)
            init_stack(args)