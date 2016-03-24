# -*- coding: utf-8 -*-

import boto3
import time
import argparse
import os

AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_REGION = os.environ['AWS_REGION']

parser = argparse.ArgumentParser()
parser.add_argument("--tag",
                    help="tag to add to all launched instances on AWS")
parser.add_argument("--nodes",
                    help="number of nodes in the cluster")
args = parser.parse_args()

if args.tag:
    tag = args.tag
else:
    # reading credentials from config for remote connection
    print('usage: python run_and_tag.py --tag <tag> --nodes <number of nodes in cluster>')
    print('reason: tag missing!!!')
    exit(1)

if args.nodes:
    nodes = int(args.nodes)
else:
    print('usage: python run_and_tag.py --tag <tag> --nodes <number of nodes in cluster>')
    print('reason: nodes missing!!!')
    exit(1)

# Connect to Amazon EC2
ec2 = boto3.resource(service_name='ec2',
                     region_name=AWS_REGION,
                     aws_access_key_id=AWS_ACCESS_KEY_ID,
                     aws_secret_access_key=AWS_SECRET_ACCESS_KEY)


for _ in range(nodes):  # = [0, 1, ..., (nodes-1)]
    # Request the launch of one instance at a time
    # (so list_of_instances should contain only one item)
    list_of_instances = ec2.create_instances(
            ImageId='ami-accff2b1',          # ubuntu-image
            # 'ami-596b7235',                 # ubuntu w/ iops storage
            MinCount=1,
            MaxCount=1,
            KeyName='bigchaindb',
            InstanceType='m3.2xlarge',
            # 'c3.8xlarge',
            # 'c4.8xlarge',
            SecurityGroupIds=['bigchaindb']
            )

    # Tag the just-launched instances (should be just one)
    for instance in list_of_instances:
        time.sleep(5)
        instance.create_tags(Tags=[{'Key': 'Name', 'Value': tag}])
