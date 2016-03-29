# -*- coding: utf-8 -*-
"""Launch the specified number of instances on Amazon EC2
and tag them with the specified tag.
"""

from __future__ import unicode_literals
import boto3
import time
import argparse
import os

AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_REGION = os.environ['AWS_REGION']

parser = argparse.ArgumentParser()
parser.add_argument("--tag",
                    help="tag to add to all launched instances on AWS",
                    required=True)
parser.add_argument("--nodes",
                    help="number of nodes in the cluster",
                    required=True,
                    type=int)
args = parser.parse_args()

tag = args.tag
num_nodes = int(args.nodes)

# Connect to Amazon EC2
ec2 = boto3.resource(service_name='ec2',
                     region_name=AWS_REGION,
                     aws_access_key_id=AWS_ACCESS_KEY_ID,
                     aws_secret_access_key=AWS_SECRET_ACCESS_KEY)


print('Starting {} instances on Amazon EC2 and tagging them with {}...'.
      format(num_nodes, tag))

for _ in range(num_nodes):
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
