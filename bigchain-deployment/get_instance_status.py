#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import boto.ec2
import time
import argparse


AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]

parser = argparse.ArgumentParser()
parser.add_argument("--tag", help="tag instances in aws")
args = parser.parse_args()

if args.tag:
    tag = args.tag
else:
    # reading credentials from config for remote connection
    print('usage: python3 get_instance_status.py --tag <tag>')
    print('reason: tag missing!!!')
    exit(1)

conn = boto.ec2.connect_to_region("eu-central-1",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

PASSING = []
RUNNING = []


# get list of instance ids from amazon
def list_of_ids(tag):
    # TODO: CHANGE TO PROPER DOCSTRING
    # Returns a list of ids of all instances with the given tag
    reservations = conn.get_all_instances(filters={"tag:Name": tag})
    # There are several reservations
    # and each reservation can have several instances
    id_list = []
    for reservation in reservations:
        for instance in reservation.instances:
            if instance.id is not None:
                id_list.append(instance.id)
    return id_list


# Andreas' old code:
"""
INSTANCE_IDS = []

def prepare_list(tag):
    reservations = conn.get_all_instances(filters={"tag:Name" : tag})
    instances = [i for r in reservations for i in r.instances]
    for i in instances:
        inst = i.__dict__
        inst_id = inst.get('id')
        INSTANCE_IDS.append(inst_id)
    return INSTANCE_IDS
"""


# get statuses from amazon
def create_run_pass_list(tag):
    # instlist_old = prepare_list(tag)
    # print("instlist_old = {}".format(instlist_old))
    instlist_new = list_of_ids(tag)
    print("instlist_new = {}".format(instlist_new))

    instlist = instlist_new

    for entry in range(0, len(instlist)):  # 0, 1, ..., [len(instlist) - 1]
        instances = conn.get_only_instances(instance_ids=instlist[entry])
        status = conn.get_all_instance_status(instance_ids=instlist[entry])
        for instance in instances:
            reachability = status[0].system_status.details["reachability"]
            PASSING.append(reachability)
    return instlist, PASSING, RUNNING


if __name__ == "__main__":
    # get lists from amazon
    try:
        instlist, passlist, runlist = create_run_pass_list(tag)
        print("instlist = {}".format(instlist))
        print("passlist = {}".format(passlist))
        print("runlist = {}".format(runlist))
    except IndexError:
        print("Searching for matching cluster-tag...")
        exit(1)

    for entry in range(0,len(instlist)):
        if "passed" in passlist and len(set(passlist)) == 1:
            print("up and running")
            exit(0)

    # exit with error code for continous check if nothing found
    exit(1)
