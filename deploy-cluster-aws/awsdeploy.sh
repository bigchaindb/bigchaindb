#! /bin/bash

# The set -e option instructs bash to immediately exit
# if any command has a non-zero exit status
set -e

# Check for the first command-line argument
# (the name of the AWS deployment config file)
if [ -z "$1" ]; then
    # no first argument was provided
    echo "awsdeploy: missing file operand"
    echo "Usage: awsdeploy DEPLOY_CONF_FILE"
    echo "Deploy BigchainDB on AWS using the specified AWS deployment configuration file"
    exit 1
fi

DEPLOY_CONF_FILE=$1

# Check to make sure DEPLOY_CONF_FILE exists
if [ ! -f "$DEPLOY_CONF_FILE" ]; then
    echo "AWS deployment configuration file not found: "$DEPLOY_CONF_FILE
    exit 1
fi

# Read DEPLOY_CONF_FILE
# to set environment variables related to AWS deployment
echo "Reading "$DEPLOY_CONF_FILE
source $DEPLOY_CONF_FILE

# Check if SSH_KEY_NAME got set
if [ "$SSH_KEY_NAME" == "not-set-yet" ] || \
   [ "$SSH_KEY_NAME" == "" ] || \
   [ -z ${SSH_KEY_NAME+x} ]; then
    echo "SSH_KEY_NAME was not set in that file"
    exit 1
fi

echo "NUM_NODES = "$NUM_NODES
echo "BRANCH = "$BRANCH
echo "WHAT_TO_DEPLOY = "$WHAT_TO_DEPLOY
echo "SSH_KEY_NAME" = $SSH_KEY_NAME
echo "USE_KEYPAIRS_FILE = "$USE_KEYPAIRS_FILE
echo "IMAGE_ID = "$IMAGE_ID
echo "INSTANCE_TYPE = "$INSTANCE_TYPE
echo "SECURITY_GROUP = "$SECURITY_GROUP
echo "USING_EBS = "$USING_EBS
if [ "$USING_EBS" = True ]; then
    echo "EBS_VOLUME_SIZE = "$EBS_VOLUME_SIZE
    echo "EBS_OPTIMIZED = "$EBS_OPTIMIZED
fi

# Check for the SSH private key file
if [ ! -f "$HOME/.ssh/$SSH_KEY_NAME" ]; then
    echo "The SSH private key file "$HOME"/.ssh/"$SSH_KEY_NAME" is missing"
    exit 1
fi

# Check for the confiles directory
if [ ! -d "confiles" ]; then
    echo "Directory confiles is needed but does not exist"
    echo "See make_confiles.sh to find out how to make it"
    exit 1
fi

# Check if NUM_NODES got set
if [ -z "$NUM_NODES" ]; then
    echo "NUM_NODES is not set in the AWS deployment configuration file "$DEPLOY_CONF_FILE
    exit 1
fi

# Check if the number of files in confiles directory == NUM_NODES
CONFILES_COUNT=`ls confiles | wc -l`
if [[ $CONFILES_COUNT != $NUM_NODES ]]; then
    echo "ERROR: CONFILES_COUNT = "$CONFILES_COUNT
    echo "but NUM_NODES = "$NUM_NODES
    echo "so there should be "$NUM_NODES" files in the confiles directory" 
    exit 1
fi

# Auto-generate the tag to apply to all nodes in the cluster
TAG="BDB-"$WHAT_TO_DEPLOY"-"`date +%m-%d@%H:%M`
echo "TAG = "$TAG

# Change the file permissions on the SSH private key file
# so that the owner can read it, but that's all
chmod 0400 $HOME/.ssh/$SSH_KEY_NAME

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
# 7. (over)writes a file named ssh_key.py
#    containing the location of the private SSH key file.
python launch_ec2_nodes.py --deploy-conf-file $DEPLOY_CONF_FILE --tag $TAG

# Make add2known_hosts.sh executable then execute it.
# This adds remote keys to ~/.ssh/known_hosts
chmod +x add2known_hosts.sh
./add2known_hosts.sh

# Test an SSH connection to one of the hosts
# and prompt the user for their SSH password if necessary
fab set_host:0 test_ssh

# Rollout base packages (dependencies) needed before
# storage backend (RethinkDB) and BigchainDB can be rolled out
fab install_base_software
fab get_pip3
fab upgrade_setuptools

if [ "$WHAT_TO_DEPLOY" == "servers" ]; then
    # (Re)create the RethinkDB configuration file conf/rethinkdb.conf
    python create_rethinkdb_conf.py
    # Rollout RethinkDB and start it
    fab prep_rethinkdb_storage:$USING_EBS
    fab install_rethinkdb
    fab configure_rethinkdb
    fab delete_rethinkdb_data
    fab start_rethinkdb
fi

# Rollout BigchainDB (but don't start it yet)
if [ "$BRANCH" == "pypi" ]; then
    fab install_bigchaindb_from_pypi
else
    cd ..
    rm -f bigchaindb-archive.tar.gz
    git archive $BRANCH --format=tar --output=bigchaindb-archive.tar
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
    if [ "$USE_KEYPAIRS_FILE" == "True" ]; then
        python clusterize_confiles.py -k confiles $NUM_NODES
    else
        python clusterize_confiles.py confiles $NUM_NODES
    fi

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
    fab set_shards:$NUM_NODES
    echo "To set the replication factor to 3, do: fab set_replicas:3"
    echo "To start BigchainDB on all the nodes, do: fab start_bigchaindb"
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
