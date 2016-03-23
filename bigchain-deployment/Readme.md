## Create and configure the storage backend in Amazon's Cloud

#### Getting started
- Checkout bigchaindb and copy bigchain-deployment to bigchaindb repository

#### Prerequesites
 - Valid AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY is needed, both are exported as variables to the shell
 - awscli,
 - boto
 - fabric w/ fabtools

#### Cluster Installation
 - Got to the DEPLOY-directory and run './startup.sh' with two parameters (tag and number of nodes)...that's it!
        e.g.: ./startup.sh bro 7 to install a cluster tagged as bro with seven nodes.

#### If an error occurs...
There are some issues during the rollout on Amazon (presumably also in other cloud/virtual environments): if you tested with a high sequence it might be possible, that you run into:
 - NetworkError: Host key for ec2-xx-xx-xx-xx.eu-central-1.compute.amazonaws.com did not match pre-existing key! Server's key was changed recently, or possible man-in-the-middle attack.
If so, just clean up your known_hosts file and start again.
