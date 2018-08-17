<!---
Copyright BigchainDB GmbH and BigchainDB contributors
SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
Code is Apache-2.0 and docs are CC-BY-4.0
--->

# Run a BigchainDB network

**NOT for Production Use**

You can use the following instructions to deploy a single or multi node
BigchainDB network for dev/test using the extensible `stack` script(s). 

Currently, this workflow is only supported for the following Operating systems:
- Ubuntu >= 16.04
- CentOS >= 7
- Fedora >= 24
- MacOSX

## Minimum Requirements
Minimum resource requirements for a single node BigchainDB dev setup. **The more the better**:
- Memory >= 512MB
- VCPUs >= 1

## Download the scripts
> **Note**: If you're working on BigchainDB Server code, on a branch based on
> recent code, then you already have local recent versions of *stack.sh* and 
> *unstack.sh* in your bigchaindb/pkg/scripts/ directory. Otherwise you can 
> get them using: 

```text
$ export GIT_BRANCH=master
$ curl -fOL https://raw.githubusercontent.com/bigchaindb/bigchaindb/${GIT_BRANCH}/pkg/scripts/stack.sh

# Optional
$ curl -fOL https://raw.githubusercontent.com/bigchaindb/bigchaindb/${GIT_BRANCH}/pkg/scripts/unstack.sh
```

## Quick Start
If you run `stack.sh` out of the box i.e. without any configuration changes, you will be able to deploy a 4 node
BigchainDB network with Docker containers, created from `master` branch of `bigchaindb/bigchaindb` repo and Tendermint version `0.22.8`.

**Note**: Run `stack.sh` with either root or non-root user with sudo enabled.

```text
$ bash stack.sh
...Logs..
.........
.........
Finished stacking!
```

## Configure the BigchainDB network

The `stack.sh` script has multiple deployment methods and parameters and they can be explored using: `bash stack.sh -h`

```text
$ bash stack.sh -h

    Usage: $ bash stack.sh [-h]

    Deploys the BigchainDB network.

    ENV[STACK_SIZE]
        Set STACK_SIZE environment variable to the size of the network you desire.
        Network mimics a production network environment with single or multiple BDB
        nodes. (default: 4).

    ENV[STACK_TYPE]
        Set STACK_TYPE environment variable to the type of deployment you desire.
        You can set it one of the following: ["docker", "local", "cloud"].
        (default: docker)

    ENV[STACK_TYPE_PROVIDER]
        Set only when STACK_TYPE="cloud". Only "azure" is supported.
        (default: )

    ENV[STACK_VM_MEMORY]
        (Optional) Set only when STACK_TYPE="local". This sets the memory
        of the instance(s) spawned. (default: 2048)

    ENV[STACK_VM_CPUS]
        (Optional) Set only when STACK_TYPE="local". This sets the number of VCPUs
        of the instance(s) spawned. (default: 2)

    ENV[STACK_BOX_NAME]
        (Optional) Set only when STACK_TYPE="local". This sets the box Vagrant box name
        of the instance(s) spawned. (default: ubuntu/xenial64)

    ENV[STACK_REPO]
        (Optional) To configure bigchaindb repo to use, set STACK_REPO environment
        variable. (default: bigchaindb/bigchaindb)

    ENV[STACK_BRANCH]
        (Optional) To configure bigchaindb repo branch to use set STACK_BRANCH environment
        variable. (default: master)

    ENV[TM_VERSION]
        (Optional) Tendermint version to use for the setup. (default: 0.22.8)

    ENV[MONGO_VERSION]
        (Optional) MongoDB version to use with the setup. (default: 3.6)

    ENV[AZURE_CLIENT_ID]
        Only required when STACK_TYPE="cloud" and STACK_TYPE_PROVIDER="azure". Steps to generate:
        https://github.com/Azure/vagrant-azure#create-an-azure-active-directory-aad-application

    ENV[AZURE_TENANT_ID]
        Only required when STACK_TYPE="cloud" and STACK_TYPE_PROVIDER="azure". Steps to generate:
        https://github.com/Azure/vagrant-azure#create-an-azure-active-directory-aad-application

    ENV[AZURE_SUBSCRIPTION_ID]
        Only required when STACK_TYPE="cloud" and STACK_TYPE_PROVIDER="azure". Steps to generate:
        https://github.com/Azure/vagrant-azure#create-an-azure-active-directory-aad-application

    ENV[AZURE_CLIENT_SECRET]
        Only required when STACK_TYPE="cloud" and STACK_TYPE_PROVIDER="azure". Steps to generate:
        https://github.com/Azure/vagrant-azure#create-an-azure-active-directory-aad-application

    ENV[AZURE_REGION]
        (Optional) Only applicable, when STACK_TYPE="cloud" and STACK_TYPE_PROVIDER="azure".
        Azure region for the BigchainDB instance. Get list of regions using Azure CLI.
        e.g. az account list-locations. (default: westeurope)

    ENV[AZURE_IMAGE_URN]
        (Optional) Only applicable, when STACK_TYPE="cloud" and STACK_TYPE_PROVIDER="azure".
        Azure image to use. Get list of available images using Azure CLI.
        e.g. az vm image list --output table. (default: Canonical:UbuntuServer:16.04-LTS:latest)

    ENV[AZURE_RESOURCE_GROUP]
        (Optional) Only applicable, when STACK_TYPE="cloud" and STACK_TYPE_PROVIDER="azure".
        Name of Azure resource group for the instance.
        (default: bdb-vagrant-rg-2018-05-30)

    ENV[AZURE_DNS_PREFIX]
        (Optional) Only applicable, when STACK_TYPE="cloud" and STACK_TYPE_PROVIDER="azure".
        DNS Prefix of the instance. (default: bdb-instance-2018-05-30)

    ENV[AZURE_ADMIN_USERNAME]
        (Optional) Only applicable, when STACK_TYPE="cloud" and STACK_TYPE_PROVIDER="azure".
        Admin username of the the instance. (default: vagrant)

    ENV[AZURE_VM_SIZE]
        (Optional) Only applicable, when STACK_TYPE="cloud" and STACK_TYPE_PROVIDER="azure".
        Azure VM size. (default: Standard_D2_v2)

    ENV[SSH_PRIVATE_KEY_PATH]
        Only required when STACK_TYPE="cloud" and STACK_TYPE_PROVIDER="azure". Absolute path of
        SSH keypair required to log into the Azure instance.

    -h
        Show this help and exit.
```


The parameter that differentiates between the deployment type is `STACK_TYPE` which currently, supports
an opinionated deployment of BigchainDB on `docker`, `local` and `cloud`. 

### STACK_TYPE: docker
This configuration deploys a docker based BigchainDB network on the dev/test machine that you are running `stack.sh` on. This is also the default `STACK_TYPE` config for `stack.sh`.

#### Example
Deploy a 4 node docker based BigchainDB network on your host.

```text
#Optional, since 4 is the default size.
$ export STACK_SIZE=4

#Optional, since docker is the default type.
$ export STACK_TYPE=docker

#Optional, repo to use for the network deployment
# Default: bigchaindb/bigchaindb
$ export STACK_REPO=bigchaindb/bigchaindb

#Optional, codebase to use for the network deployment
# Default: master
$ export STACK_BRANCH=master

#Optional, since 0.22.8 is the default tendermint version.
$ export TM_VERSION=0.22.8

#Optional, since 3.6 is the default MongoDB version.
$ export MONGO_VERSION=3.6

$ bash stack.sh
```

**Note**: For MacOSX users, the script will not install `Docker for Mac`, it only detects if `docker` is installed on the system, if not make sure to install [Docker for Mac](https://docs.docker.com/docker-for-mac/). Also make sure Docker API Version > 1.25. To check Docker API Version: 

`docker version --format '{{.Server.APIVersion}}'`

### STACK_TYPE: local
This configuration deploys a VM based BigchainDB network on your host/dev. All the services are running as processes on the VMs. For `local` deployments the following dependencies must be installed i.e.

- Vagrant
  - Vagrant plugins.
    - vagrant-cachier
    - vagrant-vbguest
    - vagrant-hosts
    - vagrant-azure
      - `vagrant plugin install vagrant-cachier vagrant-vbguest vagrant-hosts vagrant-azure`
- [Virtualbox](https://www.virtualbox.org/wiki/Downloads)

#### Example
Deploy a 4 node VM based BigchainDB network.

```text
$ export STACK_TYPE=local

# Optional, since 4 is the default size.
$ export STACK_SIZE=4

# Optional, default is 2048
$ export STACK_VM_MEMORY=2048 

#Optional, default is 1
$ export STACK_VM_CPUS=1

#Optional, default is ubuntu/xenial64. Supported/tested images: bento/centos-7, fedora/25-cloud-base
$ export STACK_BOX_NAME=ubuntu/xenial64

#Optional, repo to use for the network deployment
# Default: bigchaindb/bigchaindb
$ export STACK_REPO=bigchaindb/bigchaindb

#Optional, codebase to use for the network deployment
# Default: master
$ export STACK_BRANCH=master

#Optional, since 0.22.8 is the default tendermint version
$ export TM_VERSION=0.22.8

#Optional, since 3.6 is the default MongoDB version.
$ export MONGO_VERSION=3.6

$ bash stack.sh
```

### STACK_TYPE: cloud

This configuration deploys a docker based BigchainDB network on a cloud instance. Currently, only Azure is supported.
For `cloud` deployments the following dependencies must be installed i.e.

- Vagrant
  - Vagrant plugins.
    - vagrant-cachier
    - vagrant-vbguest
    - vagrant-hosts
    - vagrant-azure
      - `vagrant plugin install vagrant-cachier vagrant-vbguest vagrant-hosts vagrant-azure`

#### Example: stack
Deploy a 4 node docker based BigchainDB network on an Azure instance.

- [Create an Azure Active Directory(AAD) Application](https://github.com/Azure/vagrant-azure#create-an-azure-active-directory-aad-application)

- Generate or specify an SSH keypair to login to the Azure instance.

  - **Example:**
  ```text
  $ ssh-keygen -t rsa -C "<name>" -f /path/to/key/<name>
  ```

- Configure parameters for `stack.sh`
```text

# After creating the AAD application with access to Azure Resource
# Group Manager for your subscription, it will return a JSON object

$ export AZURE_CLIENT_ID=<value from azure.appId>

$ export AZURE_TENANT_ID=<value from azure.tenant>

# Can be retrieved via
# az account list --query "[?isDefault].id" -o tsv
$ export AZURE_SUBSCRIPTION_ID=<your Azure subscription ID>

$ export AZURE_CLIENT_SECRET=<value from azure.password>

$ export STACK_TYPE=cloud

# Currently on azure is supported
$ export STACK_TYPE_PROVIDER=azure

$ export SSH_PRIVATE_KEY_PATH=</path/to/private/key>

# Optional, Azure region of the instance. Default: westeurope
$ export AZURE_REGION=westeurope

# Optional, Azure image urn of the instance. Default: Canonical:UbuntuServer:16.04-LTS:latest
$ export AZURE_IMAGE_URN=Canonical:UbuntuServer:16.04-LTS:latest

# Optional, Azure resource group. Default: bdb-vagrant-rg-yyyy-mm-dd(current date)
$ export AZURE_RESOURCE_GROUP=bdb-vagrant-rg-2018-01-01

# Optional, DNS prefix of the Azure instance. Default: bdb-instance-yyyy-mm-dd(current date)
$ export AZURE_DNS_PREFIX=bdb-instance-2018-01-01

# Optional, Admin username of the Azure instance. Default: vagrant
$ export AZURE_ADMIN_USERNAME=vagrant

# Optional, Azure instance size. Default: Standard_D2_v2
$ export AZURE_VM_SIZE=Standard_D2_v2

$ bash stack.sh
```

## Delete/Unstack a BigchainDB network

Export all the variables exported for the corresponding `stack.sh` script and
run `unstack.sh` to delete/remove/unstack the BigchainDB network/stack.

```text
$ bash unstack.sh

OR

# -s implies soft unstack. i.e. Only applicable for local and cloud based
# networks. Only deletes/stops the docker(s)/process(es) and does not
# delete the instances created via Vagrant or on Cloud. Default: hard
$ bash unstack.sh -s
```
