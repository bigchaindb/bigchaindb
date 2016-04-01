# Deploy a Cluster on AWS

This section explains a way to deploy a cluster of BigchainDB nodes on Amazon Web Services (AWS). We use some Bash and Python scripts to launch several instances (virtual servers) on Amazon Elastic Compute Cloud (EC2). Then we use Fabric to install RethinkDB and BigchainDB on all those instances.

**NOTE: At the time of writing, these script _do_ launch a bunch of EC2 instances, and they do install RethinkDB plus BigchainDB on each instance, but don't expect to be able to use the cluster for anything useful. There are several issues related to configuration, networking, and external clients that must be sorted out first. That said, you might find it useful to try out the AWS deployment scripts, because setting up to use them, and using them, will be very similar once those issues get sorted out.**

## Why?

You might ask why one would want to deploy a centrally-controlled BigchainDB cluster. Isn't BigchainDB supposed to be decentralized, where each node is controlled by a different person or organization?

That's true, but there are some reasons why one might want a centrally-controlled cluster: 1) for testing, and 2) for initial deployment. Afterwards, the control of each node can be handed over to a different entity.

## Python Setup

The instructions that follow have been tested on Ubuntu 14.04, but may also work on similar distros or operating systems.

Our Python scripts for deploying to AWS use Python 2, so maybe create a Python 2 virtual environment and activate it. Then install the following Python packages (in that virtual environment):
```text
pip install fabric
pip install fabtools
pip install requests
pip install boto3
```

What did you just install?

* "[Fabric](http://www.fabfile.org/) is a Python (2.5-2.7) library and command-line tool for streamlining the use of SSH for application deployment or systems administration tasks."
* [fabtools](https://github.com/ronnix/fabtools) are "tools for writing awesome Fabric files"
* [requests](http://docs.python-requests.org/en/master/) is a Python package/library for sending HTTP requests
* "[Boto](https://boto3.readthedocs.org/en/latest/) is the Amazon Web Services (AWS) SDK for Python, which allows Python developers to write software that makes use of Amazon services like S3 and EC2." (`boto3` is the name of the latest Boto package.)

Note: You _don't_ need to install `awscli` (AWS Command-Line Interface tools) but you can if you like.

## AWS Setup

Before you can deploy a BigchainDB cluster on AWS, you must have an AWS account. If you don't already have one, you can [sign up for one for free](https://aws.amazon.com/).

### Create an AWS Access Key

The next thing you'll need is an AWS access key. If you don't have one, you can create one using the [instructions in the AWS documentation](http://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSGettingStartedGuide/AWSCredentials.html). You should get an access key ID (e.g. AKIAIOSFODNN7EXAMPLE) and a secret access key (e.g. wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY).

Our AWS deployment scripts read the AWS access key information from environment variables. One way to set the appropriate environment variables is to edit your `~/.bashrc` file (or similar) by adding the lines:
```text
export AWS_ACCESS_KEY_ID=[[insert AWS access key here, with no brackets]]
export AWS_SECRET_ACCESS_KEY=[[insert AWS secret access key here, with no brackets]]
export AWS_REGION=eu-central-1
```

You can change the `AWS_REGION` to a different one if you like. (It's where the cluster will be deployed.) The AWS documentation has [a list of them](http://docs.aws.amazon.com/general/latest/gr/rande.html#ec2_region).

You can force your terminal to re-read `~/.bashrc` by using
```text
source ~/.bashrc
```

or by opening a new terminal session.

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


## Deployment

Here's an example of how one could launch a BigchainDB cluster of 4 nodes tagged `wrigley` on AWS:
```text
cd bigchaindb
cd deploy-cluster-aws
./startup.sh wrigley 4
```

`startup.sh` is a Bash script which calls some Python 2 and Fabric scripts. Here's what it does:

0. allocates more elastic IP addresses if necessary,
1. launches the specified number of nodes (instances) on Amazon EC2,
2. tags them with the specified tag,
3. waits until those instances exist and are running,
4. for each instance, it associates an elastic IP address with that instance,
5. adds remote keys to `~/.ssh/known_hosts`,
6. (re)creates the RethinkDB configuration file `conf/rethinkdb.conf`,
7. installs base (prerequisite) software on all instances,
8. installs RethinkDB on all instances,
9. installs BigchainDB on all instances,
10. generates the genesis block,
11. starts BigchainDB on all instances.

It should take a few minutes for the deployment to finish. Once it's finished, you can login to your AWS EC2 Console (on the web) to see the instances just launched.

There are fees associated with running instances on EC2, so if you're not using them, you should terminate them. You can do that from the AWS EC2 Console.

The same is true of your allocated elastic IP addresses. There's a small fee to keep them allocated if they're not associated with a running instance. You can release them from the AWS EC2 Console.

## Known Issues

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

### Failure when Installing Base Software

If you get an error with installing the base software on the instances, then just terminate your instances and try deploying again with a different tag.
