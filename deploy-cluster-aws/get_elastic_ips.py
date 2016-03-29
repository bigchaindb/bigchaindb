# -*- coding: utf-8 -*-

""" Create Elastic IPs and assign them to instances if needed.
"""

from __future__ import unicode_literals
import os
import boto3
import argparse
import time

AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_REGION = os.environ['AWS_REGION']

parser = argparse.ArgumentParser()
parser.add_argument("--tag", help="tag instances in aws")
args = parser.parse_args()

if args.tag:
    tag = args.tag
else:
    # reading credentials from config for remote connection
    print('usage: python get_elastic_ips.py --tag <tag>')
    print('reason: tag missing!!!')
    exit(1)

# Connect to Amazon EC2
ec2 = boto3.resource(service_name='ec2',
                     region_name=AWS_REGION,
                     aws_access_key_id=AWS_ACCESS_KEY_ID,
                     aws_secret_access_key=AWS_SECRET_ACCESS_KEY)


# Get a list of all instances with the specified tag.
# (Technically, instances_with_tag is an ec2.instancesCollection.)
instances_with_tag = ec2.instances.filter(
    Filters=[{'Name': 'tag:Name', 'Values': [tag]}]
    )

print('Allocating elastic IP addresses and assigning them to the instances...')

for instance in instances_with_tag:
    # Create a client from the ec2 resource
    # See http://boto3.readthedocs.org/en/latest/guide/clients.html
    client = ec2.meta.client

    # Acquire an Elastic IP address
    # response is a dict. See http://tinyurl.com/z2n7u9k
    response = client.allocate_address(DryRun=False, Domain='standard')
    public_ip = response['PublicIp']
    print('public_ip = {}'.format(public_ip))

    # Associate that Elastic IP address with an instance
    response2 = client.associate_address(
        DryRun=False,
        InstanceId=instance.instance_id,
        PublicIp=public_ip
        )
    print('was associated with the instance with id {}'.
          format(instance.instance_id))

# Make sure all IP addresses are assigned...
print('Waiting 30 seconds to make sure all IP addresses are assigned...')
time.sleep(30)
