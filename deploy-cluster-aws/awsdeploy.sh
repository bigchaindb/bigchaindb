#! /bin/bash

# The set -e option instructs bash to immediately exit
# if any command has a non-zero exit status
set -e

USAGE="usage: ./awsdeploy.sh <number_of_nodes_in_cluster> <pypi_or_branch> <servers_or_clients>"

if [ -z "$1" ]; then
    echo $USAGE
    echo "No first argument was specified"
    echo "It should be a number like 3 or 15"
    exit 1
else
    NUM_NODES=$1
fi

if [ -z "$2" ]; then
    echo $USAGE
    echo "No second argument was specified, so BigchainDB will be installed from PyPI"
    BRANCH="pypi"
else
    BRANCH=$2
fi

if [ -z "$3" ]; then
    echo $USAGE
    echo "No third argument was specified, so servers will be deployed"
    WHAT_TO_DEPLOY="servers"
else
    WHAT_TO_DEPLOY=$3
fi

if [[ ("$WHAT_TO_DEPLOY" != "servers") && ("$WHAT_TO_DEPLOY" != "clients") ]]; then
    echo "The third argument, if included, must be servers or clients"
    exit 1
fi

# Check for AWS private key file (.pem file)
if [ ! -f "pem/bigchaindb.pem" ]; then
    echo "File pem/bigchaindb.pem (AWS private key) is missing"
    exit 1
fi

# Check for the confiles directory
if [ ! -d "confiles" ]; then
    echo "Directory confiles is needed but does not exist"
    echo "See make_confiles.sh to find out how to make it"
    exit 1
fi

# Auto-generate the tag to apply to all nodes in the cluster
TAG="BDB-"$WHAT_TO_DEPLOY"-"`date +%m-%d@%H:%M`
echo "TAG = "$TAG

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
python launch_ec2_nodes.py --tag $TAG --nodes $NUM_NODES

# Make add2known_hosts.sh executable then execute it.
# This adds remote keys to ~/.ssh/known_hosts
chmod +x add2known_hosts.sh
./add2known_hosts.sh

# Rollout base packages (dependencies) needed before
# storage backend (RethinkDB) and BigchainDB can be rolled out
fab install_base_software

if [ "$WHAT_TO_DEPLOY" == "servers" ]; then
    # (Re)create the RethinkDB configuration file conf/rethinkdb.conf
    python create_rethinkdb_conf.py
    # Rollout storage backend (RethinkDB) and start it
    fab install_rethinkdb
fi

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

if [ "$WHAT_TO_DEPLOY" == "servers" ]; then
    # The idea is to send a bunch of locally-created configuration
    # files out to each of the instances / nodes.

    # Assume a set of $NUM_NODES BigchaindB config files
    # already exists in the confiles directory.
    # One can create a set using a command like
    # ./make_confiles.sh confiles $NUM_NODES
    # (We can't do that here now because this virtual environment
    # is a Python 2 environment that may not even have
    # bigchaindb installed, so bigchaindb configure can't be called)

    # Transform the config files in the confiles directory
    # to have proper keyrings, api_endpoint values, etc.
    python clusterize_confiles.py confiles $NUM_NODES

    # Send one of the config files to each instance
    for (( HOST=0 ; HOST<$NUM_NODES ; HOST++ )); do
        CONFILE="bcdb_conf"$HOST
        echo "Sending "$CONFILE
        fab set_host:$HOST send_confile:$CONFILE
    done

    # Initialize BigchainDB (i.e. Create the RethinkDB database,
    # the tables, the indexes, and genesis glock). Note that
    # this will only be sent to one of the nodes, see the
    # definition of init_bigchaindb() in fabfile.py to see why.
    fab init_bigchaindb
    fab configure_sharding:$NUM_NODES
else
    # Deploying clients
    # The only thing to configure on clients is the api_endpoint
    # It should be the public DNS name of a BigchainDB server
    fab send_client_confile:client_confile

    # Start sending load from the clients to the servers
    fab start_bigchaindb_load
fi

# cleanup
rm add2known_hosts.sh
