# -*- coding: utf-8 -*-
"""A Fabric fabfile with functionality to prepare, install, and configure
BigchainDB, including its storage backend (RethinkDB).
"""

from __future__ import with_statement, unicode_literals

from fabric.api import sudo, env, hosts
from fabric.api import task, parallel
from fabric.contrib.files import sed
from fabric.operations import run, put
from fabric.context_managers import settings

from hostlist import public_dns_names

# Ignore known_hosts
# http://docs.fabfile.org/en/1.10/usage/env.html#disable-known-hosts
env.disable_known_hosts = True

# What remote servers should Fabric connect to? With what usernames?
env.user = 'ubuntu'
env.hosts = public_dns_names

# SSH key files to try when connecting:
# http://docs.fabfile.org/en/1.10/usage/env.html#key-filename
env.key_filename = 'pem/bigchaindb.pem'

newrelic_license_key = 'you_need_a_real_license_key'


######################################################################

# DON'T PUT @parallel
@task
def set_host(host_index):
    """A helper task to change env.hosts from the
    command line. It will only "stick" for the duration
    of the fab command that called it.

    Args:
        host_index (int): 1, 2, 3, etc.
    Example:
        fab set_host:4 fab_task_A fab_task_B
        will set env.hosts = [public_dns_names[3]]
        but only for doing fab_task_A and fab_task_B
    """
    env.hosts = [public_dns_names[int(host_index) - 1]]
    print('Set env.hosts = {}'.format(env.hosts))


# Install base software
@task
@parallel
def install_base_software():
    # new from Troy April 5, 2016. Why? See http://tinyurl.com/lccfrsj
    # sudo('rm -rf /var/lib/apt/lists/*')
    # sudo('apt-get -y clean')
    # from before:
    sudo('apt-get -y update')
    sudo('dpkg --configure -a')
    sudo('apt-get -y -f install')
    sudo('apt-get -y install build-essential wget bzip2 ca-certificates \
                     libglib2.0-0 libxext6 libsm6 libxrender1 \
                     git gcc g++ python3-dev libboost-python-dev \
                     software-properties-common python-software-properties \
                     python3-setuptools ipython3 sysstat s3cmd')
    sudo('easy_install3 pip')
    sudo('pip install -U pip wheel setuptools')


# Install RethinkDB
@task
@parallel
def install_rethinkdb():
    """Installation of RethinkDB"""
    with settings(warn_only=True):
        # preparing filesystem
        sudo("mkdir -p /data")
        # Locally mounted storage (m3.2xlarge, but also c3.xxx)
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
        put('conf/rethinkdb.conf',
            '/etc/rethinkdb/instances.d/instance1.conf',
            mode=0600,
            use_sudo=True)
        # initialize data-dir
        sudo('rm -rf /data/*')
        # finally restart instance
        sudo('/etc/init.d/rethinkdb restart')


# Install BigchainDB from PyPI
@task
@parallel
def install_bigchaindb_from_pypi():
    sudo('pip3 install bigchaindb')


# Install BigchainDB from a Git archive file
# named bigchaindb-archive.tar.gz
@task
@parallel
def install_bigchaindb_from_git_archive():
    put('bigchaindb-archive.tar.gz')
    run('tar xvfz bigchaindb-archive.tar.gz')
    sudo('pip3 install .')
    # sudo('python3 setup.py install')


# Configure BigchainDB
@task
@parallel
def configure_bigchaindb():
    run('bigchaindb -y configure', pty=False)


# Send the specified configuration file to
# the remote host and save it there in
# ~/.bigchaindb
# Use in conjunction with set_host()
# No @parallel
@task
def send_confile(confile):
    put('confiles/' + confile, 'tempfile')
    sudo('mv tempfile ~/.bigchaindb')
    print('When confile = {} '.format(confile))
    print('bigchaindb show-config output is:')
    run('bigchaindb show-config')
    print(' ')


# Initialize BigchainDB
# i.e. create the database, the tables,
# the indexes, and the genesis block.
# (The @hosts decorator is used to make this
# task run on only one node. See http://tinyurl.com/h9qqf3t )
@task
@hosts(public_dns_names[0])
def init_bigchaindb():
    run('bigchaindb init', pty=False)


# Start BigchainDB using screen
@task
@parallel
def start_bigchaindb():
    sudo('screen -d -m bigchaindb -y start &', pty=False)


# Install and run New Relic
@task
def install_newrelic():
    with settings(warn_only=True):
        sudo('echo deb http://apt.newrelic.com/debian/ newrelic non-free >> /etc/apt/sources.list')
        # sudo('apt-key adv --keyserver hkp://subkeys.pgp.net --recv-keys 548C16BF')
        sudo('apt-get update')
        sudo('apt-get -y --force-yes install newrelic-sysmond')
        sudo('nrsysmond-config --set license_key=' + newrelic_license_key)
        sudo('/etc/init.d/newrelic-sysmond restart')


###########################
# Security / Firewall Stuff
###########################

@task
def harden_sshd():
    """Security harden sshd.
    """
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
    account and then running ``sudo su -``.
    """
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
# Some helper-functions to handle bad behavior of cluster
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
