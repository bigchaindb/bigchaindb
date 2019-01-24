<!---
Copyright BigchainDB GmbH and BigchainDB contributors
SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
Code is Apache-2.0 and docs are CC-BY-4.0
--->

# Basic AWS Setup

Before you can deploy anything on AWS, you must do a few things.

## Get an AWS Account

If you don't already have an AWS account, you can [sign up for one for free at aws.amazon.com](https://aws.amazon.com/).

## Install the AWS Command-Line Interface

To install the AWS Command-Line Interface (CLI), just do:

```text
pip install awscli
```

## Create an AWS Access Key

The next thing you'll need is AWS access keys (access key ID and secret access key). If you don't have those, see [the AWS documentation about access keys](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#access-keys-and-secret-access-keys).

You should also pick a default AWS region name (e.g. `eu-central-1`). The AWS documentation has [a list of them](http://docs.aws.amazon.com/general/latest/gr/rande.html#ec2_region).

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

## Generate an RSA Key Pair for SSH

Eventually, you'll have one or more instances (virtual machines) running on AWS and you'll want to SSH to them. To do that, you need a public/private key pair. The public key will be sent to AWS, and you can tell AWS to put it in any instances you provision there. You'll keep the private key on your local workstation.

See the [page about how to generate a key pair for SSH](generate-key-pair-for-ssh).

## Send the Public Key to AWS

To send the public key to AWS, use the AWS Command-Line Interface:

```text
aws ec2 import-key-pair \
--key-name "<key-name>" \
--public-key-material file://~/.ssh/<key-name>.pub
```

If you're curious why there's a `file://` in front of the path to the public key, see issue [aws/aws-cli#41 on GitHub](https://github.com/aws/aws-cli/issues/41).

If you want to verify that your key pair was imported by AWS, go to [the Amazon EC2 console](https://console.aws.amazon.com/ec2/v2/home), select the region you gave above when you did `aws configure` (e.g. eu-central-1), click on **Key Pairs** in the left sidebar, and check that `<key-name>` is listed.
