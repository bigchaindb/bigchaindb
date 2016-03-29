# -*- coding: utf-8 -*-

# from __future__ import unicode_literals
import argparse
import boto3
import os

AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_REGION = os.environ['AWS_REGION']

parser = argparse.ArgumentParser()
parser.add_argument("--tag",
                    help="tag instances in aws",
                    required=True)
args = parser.parse_args()

tag = args.tag

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

publist = []
for instance in instances_with_tag:
    public_dns_name = getattr(instance, 'public_dns_name', None)
    if public_dns_name is not None:
        publist.append(public_dns_name)

# Create shellscript add2known_hosts.sh for adding remote keys to known_hosts
with open('add2known_hosts.sh', 'w') as f:
    f.write('#! /bin/bash\n')
    for public_dns_name in publist:
        f.write('ssh-keyscan ' + public_dns_name + ' >> ~/.ssh/known_hosts\n')

# Create a file named add2dbconf, overwriting one if it already exists
with open('add2dbconf', 'w') as f:
    f.write('## The host:port of a node that RethinkDB will connect to\n')
    for public_dns_name in publist:
        f.write('join=' + public_dns_name + ':29015\n')

# Note: The original code by Andreas wrote a file with lines of the form
#       join=public_dns_name_0:29015
#       join=public_dns_name_1:29015
#       but it stopped about halfway through the list of public_dns_names
#       (publist). In principle, it's only strictly necessary to
#       have one join= line.
#       Maybe Andreas thought that more is better, but all is too much?
#       Below is Andreas' original code. -Troy
# localFile = open('add2dbconf', 'w')
# before = 'join='
# after = ':29015'
# localFile.write('## The host:port of a node that rethinkdb will connect to\n')
# for entry in range(0,int(len(publist)/2)):
#     localFile.write(before + publist[entry] + after + '\n')

# Create a file named hostlist.py, overwriting one if it already exists
with open('hostlist.py', 'w') as f:
    f.write('hosts_dev = {}'.format(publist))
