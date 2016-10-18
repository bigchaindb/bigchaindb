# -*- coding: utf-8 -*-
"""A Fabric fabfile with functionality to prepare, install, and configure
BigchainDB, including its storage backend (RethinkDB).
"""

from __future__ import with_statement, unicode_literals

from os import environ  # a mapping (like a dict)
import sys

from fabric.api import sudo, env, hosts
from fabric.api import task, parallel
from fabric.contrib.files import sed
from fabric.operations import run, put
from fabric.context_managers import settings

from hostlist import public_dns_names
from ssh_key import ssh_key_path

# Ignore known_hosts
# http://docs.fabfile.org/en/1.10/usage/env.html#disable-known-hosts
env.disable_known_hosts = True

# What remote servers should Fabric connect to? With what usernames?
env.user = 'ubuntu'
env.hosts = public_dns_names

# SSH key files to try when connecting:
# http://docs.fabfile.org/en/1.10/usage/env.html#key-filename
env.key_filename = ssh_key_path


######################################################################

# DON'T PUT @parallel
@task
def set_host(host_index):
    """A helper task to change env.hosts from the
    command line. It will only "stick" for the duration
    of the fab command that called it.

    Args:
        host_index (int): 0, 1, 2, 3, etc.
    Example:
        fab set_host:4 fab_task_A fab_task_B
        will set env.hosts = [public_dns_names[4]]
        but only for doing fab_task_A and fab_task_B
    """
    env.hosts = [public_dns_names[int(host_index)]]


@task
def test_ssh():
    run('echo "If you see this, then SSH to a remote host worked."')


# Install base software
@task
@parallel
def install_base_software():
    # This deletes the dir where "apt-get update" stores the list of packages
    sudo('rm -rf /var/lib/apt/lists/')
    # Re-create that directory, and its subdirectory named "partial"
    sudo('mkdir -p /var/lib/apt/lists/partial/')
    # Repopulate the list of packages in /var/lib/apt/lists/
    # See https://tinyurl.com/zjvj9g3
    sudo('apt-get -y update')
    # Configure all unpacked but unconfigured packages.
    # See https://tinyurl.com/zf24hm5
    sudo('dpkg --configure -a')
    # Attempt to correct a system with broken dependencies in place.
    # See https://tinyurl.com/zpktd7l
    sudo('apt-get -y -f install')
    # For some reason, repeating the last three things makes this
    # installation process more reliable...
    sudo('apt-get -y update')
    sudo('dpkg --configure -a')
    sudo('apt-get -y -f install')
    # Install the base dependencies not already installed.
    sudo('apt-get -y install git g++ python3-dev libffi-dev')
    sudo('apt-get -y -f install')


# Get an up-to-date Python 3 version of pip
@task
@parallel
def get_pip3():
    # One way:
    # sudo('apt-get -y install python3-setuptools')
    # sudo('easy_install3 pip')
    # Another way:
    sudo('apt-get -y install python3-pip')
    # Upgrade pip
    sudo('pip3 install --upgrade pip')
    # Check the version of pip3
    run('pip3 --version')


# Upgrade setuptools
@task
@parallel
def upgrade_setuptools():
    sudo('pip3 install --upgrade setuptools')


# Prepare RethinkDB storage
@task
@parallel
def prep_rethinkdb_storage(USING_EBS):
    """Prepare RethinkDB storage"""
    # Convert USING_EBS from a string to a bool
    USING_EBS = (USING_EBS.lower() == 'true')

    # Make the /data directory for RethinkDB data
    sudo("mkdir -p /data")

    # OLD: with settings(warn_only=True):
    if USING_EBS:  # on /dev/xvdp
        # See https://tinyurl.com/h2nut68
        sudo("mkfs -t ext4 /dev/xvdp")
        sudo("mount /dev/xvdp /data")
        # To mount this EBS volume on every system reboot,
        # add an entry for the device to the /etc/fstab file.
        # First, make a copy of the current /etc/fstab file
        sudo("cp /etc/fstab /etc/fstab.orig")
        # Append a line to /etc/fstab
        sudo("echo '/dev/xvdp  /data  ext4  defaults,nofail,nobootwait  0  2' >> /etc/fstab")
        # Veryify the /etc/fstab file. If something is wrong with it,
        # then this should produce an error:
        sudo("mount -a")
        # Set the I/O scheduler for /dev/xdvp to deadline
        with settings(sudo_user='root'):
            sudo("echo deadline > /sys/block/xvdp/queue/scheduler")
    else:  # not using EBS.
        # Using the "instance store" that comes with the instance.
        # If the instance store comes with more than one volume,
        # this only mounts ONE of them: /dev/xvdb
        # For example, m3.2xlarge instances have /dev/xvdb and /dev/xvdc
        #  and /mnt is mounted on /dev/xvdb by default.
        try:
            sudo("umount /mnt")
            sudo("mkfs -t ext4 /dev/xvdb")
            sudo("mount /dev/xvdb /data")
        except:
            pass
        sudo("rm -rf /etc/fstab")
        sudo("echo 'LABEL=cloudimg-rootfs	/	 ext4     defaults,discard    0   0' >> /etc/fstab")
        sudo("echo '/dev/xvdb  /data        ext4    defaults,noatime    0   0' >> /etc/fstab")
        # Set the I/O scheduler for /dev/xdvb to deadline
        with settings(sudo_user='root'):
            sudo("echo deadline > /sys/block/xvdb/queue/scheduler")


# Install RethinkDB
@task
@parallel
def install_rethinkdb():
    """Install RethinkDB"""
    sudo("echo 'deb http://download.rethinkdb.com/apt trusty main' | sudo tee /etc/apt/sources.list.d/rethinkdb.list")
    sudo("wget -qO- http://download.rethinkdb.com/apt/pubkey.gpg | sudo apt-key add -")
    sudo("apt-get update")
    sudo("apt-get -y install rethinkdb")
    # Change owner:group of the RethinkDB data directory to rethinkdb:rethinkdb
    sudo('chown -R rethinkdb:rethinkdb /data')


# Configure RethinkDB
@task
@parallel
def configure_rethinkdb():
    """Copy the RethinkDB config file to the remote host"""
    put('conf/rethinkdb.conf',
        '/etc/rethinkdb/instances.d/instance1.conf',
        mode=0600,
        use_sudo=True)


# Delete RethinkDB data
@task
@parallel
def delete_rethinkdb_data():
    """Delete the contents of the RethinkDB /data directory
    but not the directory itself.
    """
    sudo('rm -rf /data/*')


# Start RethinkDB
@task
@parallel
def start_rethinkdb():
    """Start RethinkDB"""
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
    run('rm bigchaindb-archive.tar.gz')


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
    run('mv tempfile ~/.bigchaindb')
    print('For this node, bigchaindb show-config says:')
    run('bigchaindb show-config')


@task
@parallel
def send_client_confile(confile):
    put(confile, 'tempfile')
    run('mv tempfile ~/.bigchaindb')
    print('For this node, bigchaindb show-config says:')
    run('bigchaindb show-config')


# Initialize BigchainDB
# i.e. create the database, the tables,
# the indexes, and the genesis block.
# (The @hosts decorator is used to make this
# task run on only one node. See http://tinyurl.com/h9qqf3t )
@task
@hosts(public_dns_names[0])
def init_bigchaindb():
    run('bigchaindb init', pty=False)


# Set the number of shards (in all tables)
@task
@hosts(public_dns_names[0])
def set_shards(num_shards):
    run('bigchaindb set-shards {}'.format(num_shards))


# Set the number of replicas (in all tables)
@task
@hosts(public_dns_names[0])
def set_replicas(num_replicas):
    run('bigchaindb set-replicas {}'.format(num_replicas))


# Start BigchainDB using screen
@task
@parallel
def start_bigchaindb():
    sudo('screen -d -m bigchaindb -y start &', pty=False)


@task
@parallel
def start_bigchaindb_load():
    sudo('screen -d -m bigchaindb load &', pty=False)


# Install and run New Relic
@task
@parallel
def install_newrelic():
    newrelic_license_key = environ.get('NEWRELIC_KEY')
    if newrelic_license_key is None:
        sys.exit('The NEWRELIC_KEY environment variable is not set')
    else:
        # Andreas had this "with settings(..." line, but I'm not sure why:
        # with settings(warn_only=True):
        # Use the installation instructions from NewRelic:
        # http://tinyurl.com/q9kyrud
        # ...with some modifications
        sudo("echo 'deb http://apt.newrelic.com/debian/ newrelic non-free' >> "
             "/etc/apt/sources.list.d/newrelic.list")
        sudo('wget -O- https://download.newrelic.com/548C16BF.gpg | '
             'apt-key add -')
        sudo('apt-get update')
        sudo('apt-get -y --force-yes install newrelic-sysmond')
        sudo('nrsysmond-config --set license_key=' + newrelic_license_key)
        sudo('/etc/init.d/newrelic-sysmond start')


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
