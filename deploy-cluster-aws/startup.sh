#! /bin/bash

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
AWS=`which aws`
FAB=`which fab`
DEPLOYDIR=`pwd`
# It seems BIGCHAINDIR was never used, but I wasn't sure
# so I just commented-out the following two lines. -Troy
#BIGCHAINDIR=`dirname $DEPLOYDIR`
#export BIGCHAINDIR

# check if awscli is installed
if [ ! -f "$AWS" ]
    then
        echo "awscli is not installed!!!"
        exit 1
fi

# checck if python-fabric is installed
if [ ! -f "$FAB" ]
    then
        echo "python-fabric is not installed!!!"
        exit 1
fi

# checking pem-file and changing access rights
if [ ! -f "pem/bigchain.pem" ]
    then
        echo "Valid key is missing!!!"
        exit 1
fi
# 0400 for pem/bigchain.pem
chmod 0400 pem/bigchain.pem

# starting and tagging instances
python3 run_and_tag.py --tag $TAG --nodes $NODES
# let's wait a minute to get the nodes ready and in status initializing
#sleep 60

# checking if instances are up and running (every 5 secs.)
RET=1
until [ ${RET} -eq 0 ]; do
    python3 get_instance_status.py --tag $TAG
    RET=$?
    sleep 5
done

# in case of elastic ips...
python3 get_elastic_ips.py --tag $TAG

# everything prepared. now wait until instances up and running!
# generate hostlist.py and add_keys.sh
python3 create_hostlist.py --tag $TAG > hostlist.py
# make add_keys executable and execute
chmod +x add2known_hosts.sh
./add2known_hosts.sh

# resetting the rethinkdb initfile and adding the nodes to join...
cp conf/bigchaindb.conf.template conf/bigchaindb.conf
cat add2dbconf >> conf/bigchaindb.conf

# rollout base packages for installation of storage and bigchain
fab install_base_software

# rollout storagebackend (rethinkdb)
fab install_rethinkdb

# rollout bigchain-reporitory
fab install_bigchain

# generate genesisblock
HORST=`tail -1 conf/bigchaindb.conf|cut -d: -f1|cut -d= -f2`
fab -H $HORST -f fab_prepare_chain.py init_bigchaindb
# initiate sharding
fab start_bigchain_nodes

# now cleanup!
rm add2known_hosts.sh add2dbconf

# DONE!
