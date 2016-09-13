# Deploy a Testing Cluster on AWS

This section explains a way to deploy a cluster of BigchainDB nodes on Amazon Web Services (AWS) for testing purposes.

## Why?

Why would anyone want to deploy a centrally-controlled BigchainDB cluster? Isn't BigchainDB supposed to be decentralized, where each node is controlled by a different person or organization?

Yes! These scripts are for deploying a testing cluster, not a production cluster.

## How?

We use some Bash and Python scripts to launch several instances (virtual servers) on Amazon Elastic Compute Cloud (EC2). Then we use Fabric to install RethinkDB and BigchainDB on all those instances.

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
* "[Boto](https://boto3.readthedocs.io/en/latest/) is the Amazon Web Services (AWS) SDK for Python, which allows Python developers to write software that makes use of Amazon services like S3 and EC2." (`boto3` is the name of the latest Boto package.)
* [The aws-cli package](https://pypi.python.org/pypi/awscli), which is an AWS Command Line Interface (CLI).


## Basic AWS Setup

See the page about [basic AWS Setup](../appendices/aws-setup.html) in the Appendices.


## Get Enough Amazon Elastic IP Addresses

The AWS cluster deployment scripts use elastic IP addresses (although that may change in the future). By default, AWS accounts get five elastic IP addresses. If you want to deploy a cluster with more than five nodes, then you will need more than five elastic IP addresses; you may have to apply for those; see [the AWS documentation on elastic IP addresses](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/elastic-ip-addresses-eip.html).

## Create an Amazon EC2 Security Group

Go to the AWS EC2 Console and select "Security Groups" in the left sidebar. Click the "Create Security Group" button. You can name it whatever you like. (Notes: The default name in the example AWS deployment configuration file is `bigchaindb`. We had problems with names containing dashes.) The description should be something to help you remember what the security group is for.

For a super lax, somewhat risky, anything-can-enter security group, add these rules for Inbound traffic:

* Type = All TCP, Protocol = TCP, Port Range = 0-65535, Source = 0.0.0.0/0
* Type = SSH, Protocol = SSH, Port Range = 22, Source = 0.0.0.0/0
* Type = All UDP, Protocol = UDP, Port Range = 0-65535, Source = 0.0.0.0/0
* Type = All ICMP, Protocol = ICMP, Port Range = 0-65535, Source = 0.0.0.0/0

(Note: Source = 0.0.0.0/0 is [CIDR notation](https://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing) for "allow this traffic to come from _any_ IP address.")

If you want to set up a more secure security group, see the [Notes for Firewall Setup](../appendices/firewall-notes.html).


## Deploy a BigchainDB Monitor

This step is optional.

One way to monitor a BigchainDB cluster is to use the monitoring setup described in the [Monitoring](monitoring.html) section of this documentation. If you want to do that, then you may want to deploy the monitoring server first, so you can tell your BigchainDB nodes where to send their monitoring data.

You can deploy a monitoring server on AWS. To do that, go to the AWS EC2 Console and launch an instance:

1. Choose an AMI: select Ubuntu Server 14.04 LTS.
2. Choose an Instance Type: a t2.micro will suffice.
3. Configure Instance Details: you can accept the defaults, but feel free to change them.
4. Add Storage: A "Root" volume type should already be included. You _could_ store monitoring data there (e.g. in a folder named `/influxdb-data`) but we will attach another volume and store the monitoring data there instead. Select "Add New Volume" and an EBS volume type.
5. Tag Instance: give your instance a memorable name.
6. Configure Security Group: choose your bigchaindb security group.
7. Review and launch your instance.

When it asks, choose an existing key pair: the one you created earlier (named `bigchaindb`).

Give your instance some time to launch and become able to accept SSH connections. You can see its current status in the AWS EC2 Console (in the "Instances" section). SSH into your instance using something like:
```text
cd deploy-cluster-aws
ssh -i pem/bigchaindb.pem ubuntu@ec2-52-58-157-229.eu-central-1.compute.amazonaws.com
```

where `ec2-52-58-157-229.eu-central-1.compute.amazonaws.com` should be replaced by your new instance's EC2 hostname. (To get that, go to the AWS EC2 Console, select Instances, click on your newly-launched instance, and copy its "Public DNS" name.)

Next, create a file system on the attached volume, make a directory named `/influxdb-data`, and set the attached volume's mount point to be `/influxdb-data`. For detailed instructions on how to do that, see the AWS documentation for [Making an Amazon EBS Volume Available for Use](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-using-volumes.html).

Then install Docker and Docker Compose:
```text
# in a Python 2.5-2.7 virtual environment where fabric, boto3, etc. are installed
fab --fabfile=fabfile-monitor.py --hosts=<EC2 hostname> install_docker
```

After Docker is installed, we can run the monitor with:
```text
fab --fabfile=fabfile-monitor.py --hosts=<EC2 hostname> run_monitor
```

For more information about monitoring (e.g. how to view the Grafana dashboard in your web browser), see the [Monitoring](monitoring.html) section of this documentation.

To configure a BigchainDB node to send monitoring data to the monitoring server, change the statsd host in the configuration of the BigchainDB node. The section on [Configuring a BigchainDB Node](../server-reference/configuration.html) explains how you can do that. (For example, you can change the statsd host in `$HOME/.bigchaindb`.)


## Deploy a BigchainDB Cluster

### Step 1

Suppose _N_ is the number of nodes you want in your BigchainDB cluster. If you already have a set of _N_ BigchainDB configuration files in the `deploy-cluster-aws/confiles` directory, then you can jump to the next step. To create such a set, you can do something like:
```text
# in a Python 3 virtual environment where bigchaindb is installed
cd bigchaindb
cd deploy-cluster-aws
./make_confiles.sh confiles 3
```

That will create three (3) _default_ BigchainDB configuration files in the `deploy-cluster-aws/confiles` directory (which will be created if it doesn't already exist). The three files will be named `bcdb_conf0`, `bcdb_conf1`, and `bcdb_conf2`.

You can look inside those files if you're curious. For example, the default keyring is an empty list. Later, the deployment script automatically changes the keyring of each node to be a list of the public keys of all other nodes. Other changes are also made. That is, the configuration files generated in this step are _not_ what will be sent to the deployed nodes; they're just a starting point.

### Step 2

Step 2 is to make an AWS deployment configuration file, if necessary. There's an example AWS configuration file named `example_deploy_conf.py`. It has many comments explaining each setting. The settings in that file are (or should be):
```text
NUM_NODES=3
BRANCH="master"
WHAT_TO_DEPLOY="servers"
SSH_KEY_NAME="not-set-yet"
USE_KEYPAIRS_FILE=False
IMAGE_ID="ami-accff2b1"
INSTANCE_TYPE="m3.2xlarge"
SECURITY_GROUP="bigchaindb"
USING_EBS=False
EBS_VOLUME_SIZE=30
EBS_OPTIMIZED=False
```

Make a copy of that file and call it whatever you like (e.g. `cp example_deploy_conf.py my_deploy_conf.py`). You can leave most of the settings at their default values, but you must change the value of `SSH_KEY_NAME` to the name of your private SSH key. You can do that with a text editor. Set `SSH_KEY_NAME` to the name you used for `<key-name>` when you generated an RSA key pair for SSH (in basic AWS setup).

If you want your nodes to have a predictable set of pre-generated keypairs, then you should 1) set `USE_KEYPAIRS_FILE=True` in the AWS deployment configuration file, and 2) provide a `keypairs.py` file containing enough keypairs for all of your nodes. You can generate a `keypairs.py` file using the `write_keypairs_file.py` script. For example:
```text
# in a Python 3 virtual environment where bigchaindb is installed
cd bigchaindb
cd deploy-cluster-aws
python3 write_keypairs_file.py 100
```

The above command generates a `keypairs.py` file with 100 keypairs. You can generate more keypairs than you need, so you can use the same list over and over again, for different numbers of servers. The deployment scripts will only use the first NUM_NODES keypairs.

### Step 3

Step 3 is to launch the nodes ("instances") on AWS, to install all the necessary software on them, configure the software, run the software, and more. Here's how you'd do that:

```text
# in a Python 2.5-2.7 virtual environment where fabric, boto3, etc. are installed
cd bigchaindb
cd deploy-cluster-aws
./awsdeploy.sh my_deploy_conf.py
# Only if you want to set the replication factor to 3
fab set_replicas:3
# Only if you want to start BigchainDB on all the nodes:
fab start_bigchaindb
```

`awsdeploy.sh` is a Bash script which calls some Python and Fabric scripts. If you're curious what it does, [the source code](https://github.com/bigchaindb/bigchaindb/blob/master/deploy-cluster-aws/awsdeploy.sh) has many explanatory comments.

It should take a few minutes for the deployment to finish. If you run into problems, see the section on **Known Deployment Issues** below.

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

You can also check out the RethinkDB web interface at port 8080 on any of the instances; just go to your web browser and visit a web address like `http://ec2-52-29-197-211.eu-central-1.compute.amazonaws.com:8080/`.

## Server Monitoring with New Relic

[New Relic](https://newrelic.com/) is a business that provides several monitoring services. One of those services, called Server Monitoring, can be used to monitor things like CPU usage and Network I/O on BigchainDB instances. To do that:

1. Sign up for a New Relic account
2. Get your New Relic license key
3. Put that key in an environment variable named `NEWRELIC_KEY`. For example, you might add a line like the following to your `~/.bashrc` file (if you use Bash): `export NEWRELIC_KEY=<insert your key here>`
4. Once you've deployed a BigchainDB cluster on AWS as above, you can install a New Relic system monitor (agent) on all the instances using:

```text
# in a Python 2.5-2.7 virtual environment where fabric, boto3, etc. are installed
fab install_newrelic
```

Once the New Relic system monitor (agent) is installed on the instances, it will start sending server stats to New Relic on a regular basis. It may take a few minutes for data to show up in your New Relic dashboard (under New Relic Servers).

## Shutting Down a Cluster

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
