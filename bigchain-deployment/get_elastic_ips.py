#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# create Elastic IPs and assign them to instances if needed
import json
import os
import boto.ec2
import argparse
import time

AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]

parser = argparse.ArgumentParser()
parser.add_argument("--tag", help="tag instances in aws")
args = parser.parse_args()

if args.tag:
    tag = args.tag
else:
    # reading credentials from config for remote connection
    print('usage: python3 get_elastic_ips.py --tag <tag>')
    print('reason: tag missing!!!')
    exit(1)

conn = boto.ec2.connect_to_region("eu-central-1",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

INSTANCE_IDS = []


def prepare_list(tag):
    reservations = conn.get_all_instances(filters={"tag:Name" : tag})
    instances = [i for r in reservations for i in r.instances]
    for i in instances:
        inst = i.__dict__
        #print (inst)
        #break
        inst_id = inst.get('id')

        INSTANCE_IDS.append(inst_id)
    return INSTANCE_IDS


def get_new_pubDNS():
    eip = conn.allocate_address()
    return eip

if __name__ == "__main__":
    # hostlist.tmp (JSON) erzeugen
    instlist = prepare_list(tag)

    for entry in range(0,len(instlist)):

        instance_id = instlist[entry]
        print(instance_id)
        newpubDNS = get_new_pubDNS()
        inID = str(newpubDNS).split(':')[1]
        print(inID)
        conn.associate_address(instance_id, public_ip=inID)

    # make sure all addresse are assigned...
    time.sleep(30)
