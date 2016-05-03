# Deploy a Cluster on AWS

This section explains a way to deploy a cluster of BigchainDB nodes on Amazon Web Services (AWS). We use some Bash and Python scripts to launch several instances (virtual servers) on Amazon Elastic Compute Cloud (EC2). Then we use Fabric to install RethinkDB and BigchainDB on all those instances.

**NOTE: At the time of writing, these script _do_ launch a bunch of EC2 instances, and they do install RethinkDB plus BigchainDB on each instance, but don't expect to be able to use the cluster for anything useful. There are several issues related to configuration, networking, and external clients that must be sorted out first. That said, you might find it useful to try out the AWS deployment scripts, because setting up to use them, and using them, will be very similar once those issues get sorted out.**

## Why?

You might ask why one would want to deploy a centrally-controlled BigchainDB cluster. Isn't BigchainDB supposed to be decentralized, where each node is controlled by a different person or organization?

That's true, but there are some reasons why one might want a centrally-controlled cluster: 1) for testing, and 2) for initial deployment. Afterwards, the control of each node can be handed over to a different entity.

## Python Setup

The instructions that follow have been tested on Ubuntu 14.04, but may also work on similar distros or operating systems.

**Note: Our Python scripts for deploying to AWS use Python 2 because Fabric doesn't work with Python 3.**

Maybe create a Python 2 virtual environment and activate it. Then install the following Python packages (in that virtual environment):
```text
pip install fabric fabtools requests boto3 awscli
```

What did you just install?

* "[Fabric](http://www.fabfile.org/) is a Python (2.5-2.7) library and command-line tool for streamlining the use of SSH for application deployment or systems administration tasks."
* [fabtools](https://github.com/ronnix/fabtools) are "tools for writing awesome Fabric files"
* [requests](http://docs.python-requests.org/en/master/) is a Python package/library for sending HTTP requests
* "[Boto](https://boto3.readthedocs.org/en/latest/) is the Amazon Web Services (AWS) SDK for Python, which allows Python developers to write software that makes use of Amazon services like S3 and EC2." (`boto3` is the name of the latest Boto package.)
* [The aws-cli package](https://pypi.python.org/pypi/awscli), which is an AWS Command Line Interface (CLI).

## AWS Setup

Before you can deploy a BigchainDB cluster on AWS, you must have an AWS account. If you don't already have one, you can [sign up for one for free](https://aws.amazon.com/).

### Create an AWS Access Key

The next thing you'll need is an AWS access key. If you don't have one, you can create one using the [instructions in the AWS documentation](http://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSGettingStartedGuide/AWSCredentials.html). You should get an access key ID (e.g. AKIAIOSFODNN7EXAMPLE) and a secret access key (e.g. wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY).

You should also pick a default AWS region name (e.g. `eu-central-1`). That's where your cluster will run. The AWS documentation has [a list of them](http://docs.aws.amazon.com/general/latest/gr/rande.html#ec2_region).

Once you've got your AWS access key, and you've picked a default AWS region name, go to a terminal session and enter:
```text
aws configure
```

and answer the four questions. For example:
```text
AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE
AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
Default region name [None]: eu-central-1
Default output format [None]: [Press Enter]
```

This writes two files: 

* `~/.aws/credentials`
* `~/.aws/config`

AWS tools and packages look for those files.

### Get Enough Amazon Elastic IP Addresses

Our AWS deployment scripts use elastic IP addresses (although that may change in the future). By default, AWS accounts get five elastic IP addresses. If you want to deploy a cluster with more than five nodes, then you will need more than five elastic IP addresses; you may have to apply for those; see [the AWS documentation on elastic IP addresses](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/elastic-ip-addresses-eip.html).

### Create an Amazon EC2 Key Pair

Go to the AWS EC2 Console and select "Key Pairs" in the left sidebar. Click the "Create Key Pair" button. Give it the name `bigchaindb`. You should be prompted to save a file named `bigchaindb.pem`. That file contains the RSA private key. (Amazon keeps the corresponding public key.) Save the file in `bigchaindb/deploy-cluster-aws/pem/bigchaindb.pem`.

You should not share your private key. 

### Create an Amazon EC2 Security Group

Go to the AWS EC2 Console and select "Security Groups" in the left sidebar. Click the "Create Security Group" button. Give it the name `bigchaindb`. The description probably doesn't matter but we also put `bigchaindb` for that.

Add some rules for Inbound traffic:

* Type = All TCP, Protocol = TCP, Port Range = 0-65535, Source = 0.0.0.0/0
* Type = SSH, Protocol = SSH, Port Range = 22, Source = 0.0.0.0/0
* Type = All UDP, Protocol = UDP, Port Range = 0-65535, Source = 0.0.0.0/0
* Type = All ICMP, Protocol = ICMP, Port Range = 0-65535, Source = 0.0.0.0/0

**Note: These rules are extremely lax! They're meant to make testing easy.** You'll want to tighten them up if you intend to have a secure cluster. For example, Source = 0.0.0.0/0 is [CIDR notation](https://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing) for "allow this traffic to come from _any_ IP address."


## AWS Deployment

### AWS Deployment Step 1

Suppose _N_ is the number of nodes you want in your BigchainDB cluster. If you already have a set of _N_ BigchainDB configuration files in the `deploy-cluster-aws/confiles` directory, then you can jump to step 2. To create such a set, you can do something like:
```text
# in a Python 3 virtual environment where bigchaindb is installed
cd bigchaindb
cd deploy-cluster-aws
./make_confiles.sh confiles 3
```

That will create three (3) _default_ BigchainDB configuration files in the `deploy-cluster-aws/confiles` directory (which will be created if it doesn't already exist). The three files will be named `bcdb_conf0`, `bcdb_conf1`, and `bcdb_conf2`.

You can look inside those files if you're curious. In step 2, they'll be modified. For example, the default keyring is an empty list. In step 2, the deployment script automatically changes the keyring of each node to be a list of the public keys of all other nodes. Other changes are also made.

### AWS Deployment Step 2

Step 2 is to launch the nodes ("instances") on AWS, to install all the necessary software on them, configure the software, run the software, and more.

Here's an example of how one could launch a BigchainDB cluster of three (3) nodes tagged `wrigley` on AWS:
```text
# in a Python 2.5-2.7 virtual environment where fabric, boto3, etc. are installed
cd bigchaindb
cd deploy-cluster-aws
./awsdeploy_servers.sh wrigley 3 pypi
```

The `pypi` on the end means that it will install the latest (stable) `bigchaindb` package from the [Python Package Index (PyPI)](https://pypi.python.org/pypi). That is, on each node, BigchainDB is installed using `pip install bigchaindb`. 

`awsdeploy_servers.sh` is a Bash script which calls some Python and Fabric scripts. The usage is:
```text
./awsdeploy_servers.sh <tag> <number_of_nodes_in_cluster> <pypi_or_branch>
```

The first two arguments are self-explanatory. The third argument can be `pypi` or the name of a local Git branch (e.g. `master` or `feat/3752/quote-asimov-on-tuesdays`). If you don't include a third argument, then `pypi` will be assumed by default.

If you're curious what the `awsdeploy_servers.sh` script does, the source code has lots of explanatory comments, so it's quite easy to read. Here's a link to the latest version on GitHub: [`awsdeploy_servers.sh`](https://github.com/bigchaindb/bigchaindb/blob/master/deploy-cluster-aws/awsdeploy_servers.sh)

It should take a few minutes for the deployment to finish. If you run into problems, see the section on Known Deployment Issues below.

The EC2 Console has a section where you can see all the instances you have running on EC2. You can `ssh` into a running instance using a command like:
```text
ssh -i pem/bigchaindb.pem ubuntu@ec2-52-29-197-211.eu-central-1.compute.amazonaws.com
```

except you'd replace the `ec2-52-29-197-211.eu-central-1.compute.amazonaws.com` with the public DNS name of the instance you want to `ssh` into. You can get that from the EC2 Console: just click on an instance and look in its details pane at the bottom of the screen. Some commands you might try:
```text
ip addr show
sudo service rethinkdb status
bigchaindb --help
bigchaindb show-config
```

There are fees associated with running instances on EC2, so if you're not using them, you should terminate them. You can do that using the AWS EC2 Console.

The same is true of your allocated elastic IP addresses. There's a small fee to keep them allocated if they're not associated with a running instance. You can release them using the AWS EC2 Console, or by using a handy little script named `release_eips.py`. For example:
```text
$ python release_eips.py
You have 2 allocated elactic IPs which are not associated with instances
0: Releasing 52.58.110.110
(It has Domain = vpc.)
1: Releasing 52.58.107.211
(It has Domain = vpc.)
```

## Known Deployment Issues

### NetworkError

If you tested with a high sequence it might be possible that you run into an error message like this:
```text
NetworkError: Host key for ec2-xx-xx-xx-xx.eu-central-1.compute.amazonaws.com 
did not match pre-existing key! Server's key was changed recently, or possible 
man-in-the-middle attack.
```

If so, just clean up your `known_hosts` file and start again. For example, you might copy your current `known_hosts` file to `old_known_hosts` like so:
```text
mv ~/.ssh/known_hosts ~/.ssh/old_known_hosts
```

Then terminate your instances and try deploying again with a different tag.

### Failure of sudo apt-get update

The first thing that's done on all the instances, once they're running, is basically [`sudo apt-get update`](http://askubuntu.com/questions/222348/what-does-sudo-apt-get-update-do). Sometimes that fails. If so, just terminate your instances and try deploying again with a different tag. (These problems seem to be time-bounded, so maybe wait a couple of hours before retrying.)

### Failure when Installing Base Software

If you get an error with installing the base software on the instances, then just terminate your instances and try deploying again with a different tag.
