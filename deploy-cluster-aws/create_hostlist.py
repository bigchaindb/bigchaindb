# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import json
import argparse
import boto.ec2
import os

AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]

parser = argparse.ArgumentParser()
parser.add_argument("--tag", help="tag instances in aws")
args = parser.parse_args()

conn = boto.ec2.connect_to_region("eu-central-1",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

PUBLIC_LIST = []
PRIVATE_LIST = []
INSTANCE_IDS = []

if args.tag:
    tag = args.tag
else:
    # reading credentials from config for remote connection
    print('usage: python3 create_hostlist.py --tag <tag>')
    print('reason: tag missing!!!')
    exit(1)


def prepare_list(tag):
    reservations = conn.get_all_instances(filters={"tag:Name" : tag})
    instances = [i for r in reservations for i in r.instances]
    for i in instances:
        inst = i.__dict__
        publdns = inst.get('public_dns_name')
        privdns = inst.get('private_dns_name')
        inst_id = inst.get('id')
        PUBLIC_LIST.append(publdns)
        PRIVATE_LIST.append(privdns)
        INSTANCE_IDS.append(inst_id)
    return PUBLIC_LIST, PRIVATE_LIST, INSTANCE_IDS


# get lists from amazon
publist, privlist, instlist = prepare_list(tag)

# create shellscript for adding remote keys to known_hosts
localFile = open('add2known_hosts.sh', 'w')
localFile.write('#! /bin/bash\n')
for entry in range(0,len(publist)):
    localFile.write('ssh-keyscan ' + publist[entry] + ' >> ~/.ssh/known_hosts\n')
localFile.close()

# hostliste und id-liste aus json erzeugen
hosts = publist
localFile = open('add2dbconf', 'w')
before = 'join='
after = ':29015'
localFile.write('## The host:port of a node that rethinkdb will connect to\n')
for entry in range(0,int(len(hosts)/2)):
    localFile.write(before + hosts[entry] + after + '\n')


# printout hostlist
print ("hosts_dev = ", publist)
