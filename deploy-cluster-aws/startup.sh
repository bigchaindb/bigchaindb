#! /bin/bash

# The set -e option instructs bash to immediately exit if any command has a non-zero exit status
set -e

function printErr()
    {
        echo "usage: ./startup.sh <tag> <number_of_nodes_in_cluster>"
        echo "No argument $1 supplied"
    }

if [ -z "$1" ]
  then
    printErr "<tag>"
    exit 1
fi

if [ -z "$2" ]
  then
    printErr "<number_of_nodes_in_cluster>"
    exit 1
fi

TAG=$1
NODES=$2
FAB=`which fab`

# It seems BIGCHAINDIR was never used, but I wasn't sure
# so I just commented-out the following lines. -Troy
#DEPLOYDIR=`pwd`
#BIGCHAINDIR=`dirname $DEPLOYDIR`
#export BIGCHAINDIR

# Check if python-fabric is installed
if [ ! -f "$FAB" ]
    then
        echo "python-fabric is not installed"
        exit 1
fi

# Check for AWS private key file  pem-file and changing access rights
if [ ! -f "pem/bigchaindb.pem" ]
    then
        echo "File pem/bigchaindb.pem (AWS private key) is missing"
        exit 1
fi

# Change the file permissions on pem/bigchaindb.pem
# so that the owner can read it, but that's all
chmod 0400 pem/bigchaindb.pem

# Start the specified number of nodes on Amazon EC2
# and tag them with the specified tag
python run_and_tag.py --tag $TAG --nodes $NODES

# Wait until all those instances are running
python wait_until_all_running.py --tag $TAG

# Allocate elastic IP addresses and assign them to the instances
python get_elastic_ips.py --tag $TAG

# Create three files:
# add2known_hosts.sh, add2dbconf and hostlist.py
python create_hostlist.py --tag $TAG

# Make add2known_hosts.sh executable and execute it
chmod +x add2known_hosts.sh
./add2known_hosts.sh

# Reset the RethinkDB configuration file and add the nodes to join
cp conf/bigchaindb.conf.template conf/bigchaindb.conf
cat add2dbconf >> conf/bigchaindb.conf

# rollout base packages (dependencies) needed before
# storage backend (rethinkdb) and bigchaindb can be rolled out
fab install_base_software

# rollout storage backend (rethinkdb)
fab install_rethinkdb

# rollout bigchaindb
fab install_bigchaindb

# generate genesis block
# HORST is the last public_dns_name listed in conf/bigchaindb.conf
# For example:
# ec2-52-58-86-145.eu-central-1.compute.amazonaws.com
HORST=`tail -1 conf/bigchaindb.conf|cut -d: -f1|cut -d= -f2`
fab -H $HORST -f fab_prepare_chain.py init_bigchaindb

# initiate sharding
fab start_bigchaindb_nodes

# cleanup
rm add2known_hosts.sh add2dbconf

# DONE
