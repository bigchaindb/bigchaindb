# AWS deployment config file

# To use in a Bash shell script:
# source example_deploy_conf.py
# # $EXAMPLEVAR now has a value

# To use in a Python script:
# from example_deploy_conf import *
# or
# import importlib
# cf = importlib.import_module('example_deploy_conf')
# # cf.EXAMPLEVAR now has a value

# DON'T PUT SPACES AROUND THE =
# because that would confuse Bash.
# Example values: "string in double quotes", 32, True, False

# NUM_NODES is the number of nodes to deploy
NUM_NODES=3

# BRANCH is either "pypi" or the name of a local Git branch
# (e.g. "master" or "feat/3627/optional-delimiter-in-txfile")
# It's where to get the BigchainDB code to be deployed on the nodes
BRANCH="master"

# WHAT_TO_DEPLOY is either "servers" or "clients"
# What do you want to deploy?
WHAT_TO_DEPLOY="servers"

# SSH_KEY_NAME is the name of the SSH private key file
# in $HOME/.ssh/
# It is used for SSH communications with AWS instances.
SSH_KEY_NAME="not-set-yet"

# USE_KEYPAIRS_FILE is either True or False
# Should node keypairs be read from keypairs.py?
# (If False, then the keypairs will be whatever is in the the
#  BigchainDB config files in the confiles directory.)
USE_KEYPAIRS_FILE=False

# IMAGE_ID is the Amazon Machine Image (AMI) id to use
# in all the servers/instances to be launched.
# Examples:
# "ami-accff2b1" = An Ubuntu 14.04.2 LTX "Ubuntu Cloud image" from Canonical
#                  64-bit, hvm-ssd, published to eu-central-1
#                  See http://tinyurl.com/hkjhg46
# "ami-596b7235" = Ubuntu with IOPS storage? Does this work?
#
# See http://cloud-images.ubuntu.com/releases/14.04/release-20150325/
IMAGE_ID="ami-accff2b1"

# INSTANCE_TYPE is the type of AWS instance to launch
# i.e. How many CPUs do you want? How much storage? etc.
# Examples: "m3.2xlarge", "c3.8xlarge", "c4.8xlarge"
# For all options, see https://aws.amazon.com/ec2/instance-types/
INSTANCE_TYPE="m3.2xlarge"

# SECURITY_GROUP is the name of the AWS security group to use.
# That security group must exist.
# Examples: "bigchaindb", "bcdbsecure"
SECURITY_GROUP="bigchaindb"

# USING_EBS is True if you want to attach an Amazon EBS volume
USING_EBS=False

# EBS_VOLUME_SIZE is the size of the EBS volume to attach, in GiB
# Since we assume 'gp2' volumes (for now), the possible range is 1 to 16384
# If USING_EBS=False, EBS_VOLUME_SIZE is irrelevant and not used
EBS_VOLUME_SIZE=30

# EBS_OPTIMIZED is True or False, depending on whether you want
# EBS-optimized instances. See:
# https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EBSOptimized.html
# Not all instance types support EBS optimization.
# Setting EBS_OPTIMIZED=True may cost more, but not always.
# If USING_EBS=False, EBS_OPTIMIZED is irrelevant and not used
EBS_OPTIMIZED=False
