#! /bin/bash

# The set -e option instructs bash to immediately exit
# if any command has a non-zero exit status
set -e

function printErr()
    {
        echo "usage: ./startup.sh <tag> <number_of_nodes_in_cluster> <pypi_or_branch>"
        echo "No argument $1 supplied"
    }

if [ -z "$1" ]; then
    printErr "<tag>"
    exit 1
fi

if [ -z "$2" ]; then
    printErr "<number_of_nodes_in_cluster>"
    exit 1
fi

TAG=$1
NODES=$2

# If they don't include a third argument (<pypi_or_branch>)
# then assume BRANCH = "pypi" by default
if [ -z "$3" ]; then
    echo "No third argument was specified, so BigchainDB will be installed from PyPI"
    BRANCH="pypi"
else
    BRANCH=$3
fi

# Check for AWS private key file (.pem file)
if [ ! -f "pem/bigchaindb.pem" ]; then
    echo "File pem/bigchaindb.pem (AWS private key) is missing"
    exit 1
fi

# Change the file permissions on pem/bigchaindb.pem
# so that the owner can read it, but that's all
chmod 0400 pem/bigchaindb.pem

# The following Python script does these things:
# 0. allocates more elastic IP addresses if necessary,
# 1. launches the specified number of nodes (instances) on Amazon EC2,
# 2. tags them with the specified tag,
# 3. waits until those instances exist and are running,
# 4. for each instance, it associates an elastic IP address
#    with that instance,
# 5. writes the shellscript add2known_hosts.sh
# 6. (over)writes a file named hostlist.py
#    containing a list of all public DNS names.
python launch_ec2_nodes.py --tag $TAG --nodes $NODES 

# Make add2known_hosts.sh executable then execute it.
# This adds remote keys to ~/.ssh/known_hosts
chmod +x add2known_hosts.sh
./add2known_hosts.sh

# (Re)create the RethinkDB configuration file conf/rethinkdb.conf
python create_rethinkdb_conf.py

# Rollout base packages (dependencies) needed before
# storage backend (RethinkDB) and BigchainDB can be rolled out
fab install_base_software

# Rollout storage backend (RethinkDB) and start it
fab install_rethinkdb

# Rollout BigchainDB (but don't start it yet)
if [ "$BRANCH" == "pypi" ]; then
    fab install_bigchaindb_from_pypi
else
    cd ..
    rm -f bigchaindb-archive.tar.gz
    git archive $BRANCH --format=tar --output=bigchaindb-archive.tar
    # TODO: the archive could exclude more files besides the .gitignore ones
    # such as the docs. See http://tinyurl.com/zo6fxeg
    gzip bigchaindb-archive.tar
    mv bigchaindb-archive.tar.gz deploy-cluster-aws
    cd deploy-cluster-aws
    fab install_bigchaindb_from_git_archive
    rm bigchaindb-archive.tar.gz
fi

# Configure BigchainDB on all nodes
fab configure_bigchaindb

# TODO: Get public keys from all nodes


# TODO: Add list of public keys to keyring of all nodes


# Send a "bigchaindb init" command to one node
# to initialize the BigchainDB database 
# i.e. create the database, the tables,
# the indexes, and the genesis block.
fab set_hosts:one_node init_bigchaindb

# Start BigchainDB on all the nodes using "screen"
fab start_bigchaindb

# cleanup
rm add2known_hosts.sh
