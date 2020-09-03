from __future__ import print_function
import json
import boto3
import boto.ec2
import logging
import time
import datetime
import types
import ec2_description

# enable logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler():
    test = ec2_description.ec2_ebs_snapshots()
    print(test)
    sts_connection = boto3.client('sts')
    logging_acct = sts_connection.assume_role(
        RoleArn="ARN OF CROSS ACCOUNT ROLE TO ASSUME",
        RoleSessionName="cross_acct_lambda"
    )

    ACCESS_KEY = logging_acct['Credentials']['AccessKeyId']
    SECRET_KEY = logging_acct['Credentials']['SecretAccessKey']
    SESSION_TOKEN = logging_acct['Credentials']['SessionToken']
    print(ACCESS_KEY)
    print(SECRET_KEY)
    print(SESSION_TOKEN)

    kinesis = boto3.client(
        'kinesis',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        aws_session_token=SESSION_TOKEN,
    )
    records = []
    count = 0
    for tes in test:
        record = { 'Data':b'tes','PartitionKey':'value1' }
        records.append(record)
        count +=1
        if count == 500:
            response = kinesis.put_records(Records=records, StreamName='KINESIS STREAM NAME')
            records = []
            count = 0

    response = kinesis.put_records(Records=records, StreamName='KINESIS STREAM NAME')
    print(response)

if __name__ == '__main__':
    lambda_handler()
