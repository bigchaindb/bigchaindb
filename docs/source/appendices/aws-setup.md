# AWS Setup 

Before you can deploy a BigchainDB node or cluster on AWS, you must do a few things.


## Get an AWS Account

If you don't already have an AWS account, you can [sign up for one for free at aws.amazon.com](https://aws.amazon.com/).


## Install the AWS Command-Line Interface

To install the AWS Command-Line Interface (CLI), just do:
```text
pip install awscli
```


## Create an AWS Access Key

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

This writes two files: `~/.aws/credentials` and `~/.aws/config`. AWS tools and packages look for those files.


## Get Enough Amazon Elastic IP Addresses

You can skip this if you're deploying a single node.

Our AWS cluster deployment scripts use elastic IP addresses (although that may change in the future). By default, AWS accounts get five elastic IP addresses. If you want to deploy a cluster with more than five nodes, then you will need more than five elastic IP addresses; you may have to apply for those; see [the AWS documentation on elastic IP addresses](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/elastic-ip-addresses-eip.html).


## Create an Amazon EC2 Key Pair

Go to the AWS EC2 Console and select "Key Pairs" in the left sidebar. Click the "Create Key Pair" button. Give it the name `bigchaindb`. You should be prompted to save a file named `bigchaindb.pem`. That file contains the RSA private key. (You can get the public key from the private key, so there's no need to send it separately.)

If you're deploying a cluster, save the file in `bigchaindb/deploy-cluster-aws/pem/bigchaindb.pem`.

If you're deploying a single node, save the file in `bigchaindb/deploy-node-aws/pem/bigchaindb.pem`.

**You should not share your private key.**


## Create an Amazon EC2 Security Group

Go to the AWS EC2 Console and select "Security Groups" in the left sidebar. Click the "Create Security Group" button. If you're deploying a cluster, give it the name `bigchaindb`, otherwise you can name it whatever you like. The description probably doesn't matter but we also put `bigchaindb` for that.

If you're deploying a test cluster, then add these rules for Inbound traffic:

* Type = All TCP, Protocol = TCP, Port Range = 0-65535, Source = 0.0.0.0/0
* Type = SSH, Protocol = SSH, Port Range = 22, Source = 0.0.0.0/0
* Type = All UDP, Protocol = UDP, Port Range = 0-65535, Source = 0.0.0.0/0
* Type = All ICMP, Protocol = ICMP, Port Range = 0-65535, Source = 0.0.0.0/0

**Note: These rules are extremely lax! They're meant to make testing easy.** For example, Source = 0.0.0.0/0 is [CIDR notation](https://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing) for "allow this traffic to come from _any_ IP address."

If you're deploying a single node, then see [the BigchainDB Notes for Firewall Setup](firewall-notes.html) and [the AWS documentation about security groups](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-network-security.html).
