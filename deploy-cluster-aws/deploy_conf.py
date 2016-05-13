# AWS deployment config file

# To use in a Bash shell script:
# source deploy_conf.py
# echo $EXAMPLEVAR

# To use in a Python script:
# from deploy_conf import *
# # EXAMPLEVAR now has a value

# DON'T PUT SPACES AROUND THE =
# because that would confuse Bash.
# Values can be strings in double quotes, or integers like 23

# NUM_NODES is the number of nodes to deploy
NUM_NODES=3

# PYPI_OR_BRANCH is either "pypi" or the name of a local Git branch
# (e.g. "master" or "feat/3627/optional-delimiter-in-txfile")
# It's where to get the BigchainDB code to be deployed on the nodes
BRANCH="master"

# WHAT_TO_DEPLOY is either "servers" or "clients"
# What do you want to deploy?
WHAT_TO_DEPLOY="servers"

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
