#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Preparing, installing and configuring
    bigchain and the storage backend
"""

from __future__ import with_statement

import requests
from time import *
import os
from datetime import datetime, timedelta
import json
from pprint import pprint

from fabric import colors as c
from fabric.api import *
from fabric.api import local, puts, settings, hide, abort, lcd, prefix
from fabric.api import run, sudo, cd, get, local, lcd, env, hide
from fabric.api import task, parallel
from fabric.contrib import files
from fabric.contrib.files import append, exists
from fabric.contrib.console import confirm
from fabric.contrib.project import rsync_project
from fabric.operations import run, put
from fabric.context_managers import settings
from fabric.decorators import roles
from fabtools import *

from hostlist import hosts_dev

env.hosts = hosts_dev
env.roledefs = {
    "role1": hosts_dev,
    "role2": [hosts_dev[0]],
    }
env.roles = ["role1"]
env.user = 'ubuntu'
env.key_filename = 'pem/bigchaindb.pem'


################################################################################

# base softwarestack rollout
@task
@parallel
def install_base_software():
    sudo('apt-get -y update')
    sudo('dpkg --configure -a')
    sudo('apt-get -y -f install')
    sudo('apt-get -y install build-essential wget bzip2 ca-certificates \
                     libglib2.0-0 libxext6 libsm6 libxrender1 libssl-dev \
                     git gcc g++ python-dev libboost-python-dev libffi-dev \
                     software-properties-common python-software-properties \
                     python3-pip ipython3 sysstat s3cmd')


# RethinkDB
@task
@parallel
def install_rethinkdb():
    """Installation of RethinkDB"""
    with settings(warn_only=True):
        # preparing filesystem
        sudo("mkdir -p /data")
        # Locally mounted storage (m3.2xlarge, aber auch c3.xxx)
        try:
            sudo("umount /mnt")
            sudo("mkfs -t ext4 /dev/xvdb")
            sudo("mount /dev/xvdb /data")
        except:
            pass

        # persist settings to fstab
        sudo("rm -rf /etc/fstab")
        sudo("echo 'LABEL=cloudimg-rootfs	/	 ext4     defaults,discard    0   0' >> /etc/fstab")
        sudo("echo '/dev/xvdb  /data        ext4    defaults,noatime    0   0' >> /etc/fstab")
        # activate deadline scheduler
        with settings(sudo_user='root'):
            sudo("echo deadline > /sys/block/xvdb/queue/scheduler")
        # install rethinkdb
        sudo("echo 'deb http://download.rethinkdb.com/apt trusty main' | sudo tee /etc/apt/sources.list.d/rethinkdb.list")
        sudo("wget -qO- http://download.rethinkdb.com/apt/pubkey.gpg | sudo apt-key add -")
        sudo("apt-get update")
        sudo("apt-get -y install rethinkdb")
        # change fs to user
        sudo('chown -R rethinkdb:rethinkdb /data')
        # copy config file to target system
        put('conf/bigchaindb.conf',
            '/etc/rethinkdb/instances.d/instance1.conf', mode=0600, use_sudo=True)
        # initialize data-dir
        sudo('rm -rf /data/*')
        # finally restart instance
        sudo('/etc/init.d/rethinkdb restart')


# bigchaindb deployment
@task
@parallel
def install_bigchaindb():
    sudo('python3 -m pip install bigchaindb')


# startup all nodes of bigchaindb in cluster
@task
@parallel
def start_bigchain_nodes():
    sudo('screen -d -m bigchaindb -y start &', pty = False)


@task
def install_newrelic():
    with settings(warn_only=True):
        sudo('echo deb http://apt.newrelic.com/debian/ newrelic non-free >> /etc/apt/sources.list')
        #sudo('apt-key adv --keyserver hkp://subkeys.pgp.net --recv-keys 548C16BF')
        sudo('apt-get update')
        sudo('apt-get -y --force-yes install newrelic-sysmond')
        sudo('nrsysmond-config --set license_key=c88af00c813983f8ee12e9b455aa13fde1cddaa8')
        sudo('/etc/init.d/newrelic-sysmond restart')


###############################
# Security / FirewallStuff next
###############################

@task
def harden_sshd():
    """Security harden sshd."""

    # Disable password authentication
    sed('/etc/ssh/sshd_config',
        '#PasswordAuthentication yes',
        'PasswordAuthentication no',
        use_sudo=True)
    # Deny root login
    sed('/etc/ssh/sshd_config',
        'PermitRootLogin yes',
        'PermitRootLogin no',
        use_sudo=True)


@task
def disable_root_login():
    """Disable `root` login for even more security. Access to `root` account
    is now possible by first connecting with your dedicated maintenance
    account and then running ``sudo su -``."""
    sudo('passwd --lock root')


@task
def set_fw():
    # snmp
    sudo('iptables -A INPUT -p tcp --dport 161 -j ACCEPT')
    sudo('iptables -A INPUT -p udp --dport 161 -j ACCEPT')
    # dns
    sudo('iptables -A OUTPUT -p udp -o eth0 --dport 53 -j ACCEPT')
    sudo('iptables -A INPUT -p udp -i eth0 --sport 53 -j ACCEPT')
    # rethinkdb
    sudo('iptables -A INPUT -p tcp --dport 28015 -j ACCEPT')
    sudo('iptables -A INPUT -p udp --dport 28015 -j ACCEPT')
    sudo('iptables -A INPUT -p tcp --dport 29015 -j ACCEPT')
    sudo('iptables -A INPUT -p udp --dport 29015 -j ACCEPT')
    sudo('iptables -A INPUT -p tcp --dport 8080 -j ACCEPT')
    sudo('iptables -A INPUT -i eth0 -p tcp --dport 8080 -j DROP')
    sudo('iptables -I INPUT -i eth0 -s 127.0.0.1 -p tcp --dport 8080 -j ACCEPT')
    # save rules
    sudo('iptables-save >  /etc/sysconfig/iptables')


#########################################################
# some helper-functions to handle bad behavior of cluster
#########################################################

# rebuild indexes
@task
@parallel
def rebuild_indexes():
    run('rethinkdb index-rebuild -n 2')


@task
def stopdb():
    sudo('service rethinkdb stop')


@task
def startdb():
    sudo('service rethinkdb start')


@task
def restartdb():
    sudo('/etc/init.d/rethinkdb restart')
