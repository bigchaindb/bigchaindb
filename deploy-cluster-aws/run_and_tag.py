#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import boto.ec2
import time
import argparse
import os

AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]

parser = argparse.ArgumentParser()
parser.add_argument("--tag", help="tag instances in aws")
parser.add_argument("--nodes", help="number of nodes in the cluster")
args = parser.parse_args()

if args.tag:
    tag = args.tag
else:
    # reading credentials from config for remote connection
    print('usage: python3 run_and_tag.py --tag <tag> --nodes <number of nodes in cluster>')
    print('reason: tag missing!!!')
    exit(1)

if args.nodes:
    nodes = int(args.nodes)
else:
    print('usage: python3 run_and_tag.py --tag <tag> --nodes <number of nodes in cluster>')
    print('reason: nodes missing!!!')
    exit(1)

conn = boto.ec2.connect_to_region("eu-central-1",
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

for _ in range(nodes):  # 0, 1, ..., (nodes-1) = nodes items
    reservation = conn.run_instances(
            'ami-accff2b1',                    # ubuntu-image
            #'ami-596b7235',                    # ubuntu w/ iops storage
            key_name='bigchaindb',
            # IMPORTANT!!!! - here you change the machine type for the cluster
            instance_type='m3.2xlarge',
            #instance_type='c3.8xlarge',
            #instance_type='c4.8xlarge',
            security_groups=['bigchain'])

    for instance in reservation.instances:
        time.sleep(5)
        instance.add_tag('Name', tag)
