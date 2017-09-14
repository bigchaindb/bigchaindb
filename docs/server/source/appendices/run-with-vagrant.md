# Run BigchainDB with Vagrant

**NOT for Production Use**

You can use the following instructions to deploy a BigchainDB node
for dev/test using Vagrant. Vagrant will setup a BigchainDB node with
all the dependencies along with MongoDB, BigchainDB Python driver. You
can also tweak the following configurations for the BigchainDB node.
- Vagrant Box
  - Currently, we support the following boxes:
    - `ubuntu/xenial64 # >=16.04`
    - `centos/7 # >=7`
    - `fedora/24 # >=24`
  - **NOTE** : You can choose any other vagrant box of your choice but these are
  the minimum versioning requirements.
- Resources and specs for your box.
  - RAM
  - VCPUs
  - Network Type
    - Currently, only `private_network` is supported.
  - IP Address
- Setup type
  - `quickstart`
- Deploy node with Docker
  - Deploy all the services in Docker containers or as processes.
- Upstart Script
- Vagrant Provider
  - Virtualbox
  - VMware

## Install dependencies | Vagrant
1. [VirtualBox](https://www.virtualbox.org/wiki/Downloads) >= 5.0.0
2. [Vagrant](https://www.vagrantup.com/downloads.html) >= 1.16.0

## Clone the BigchainDB repository | Vagrant
```text
$ git clone https://github.com/bigchaindb/bigchaindb.git
```

## Configuration | Vagrant
Navigate to `bigchaindb/pkg/config/` inside the repository.
```text
$ cd bigchaindb/pkg/config/
```

Edit the `bdb-config.yaml` as per your requirements. Sample `bdb-config.yaml`:

```text
---
- name: "bdb-node-01"
  box:
    name: "ubuntu/xenial64"
  ram: "2048"
  vcpus: "2"
  setup_type: "quickstart"
  deploy_docker: false
  network:
    ip: "10.20.30.40"
    type: "private_network"
  upstart: "/bigchaindb/scripts/bootstrap.sh"
```

**Note**: You can spawn multiple instances as well using `bdb-config.yaml`. Here is a sample `bdb-config.yaml`:
```text
---
- name: "bdb-node-01"
  box:
    name: "ubuntu/xenial64"
  ram: "2048"
  vcpus: "2"
  setup_type: "quickstart"
  deploy_docker: false
  network:
    ip: "10.20.30.40"
    type: "private_network"
  upstart: "/bigchaindb/scripts/bootstrap.sh"
- name: "bdb-node-02"
  box:
    name: "ubuntu/xenial64"
  ram: "4096"
  vcpus: "3"
  setup_type: "quickstart"
  deploy_docker: false
  network:
    ip: "10.20.30.50"
    type: "private_network"
  upstart: "/bigchaindb/scripts/bootstrap.sh"
```


## Local Setup | Vagrant
To bring up the BigchainDB node, run the following command:

```text
$ vagrant up
```

*Note*: There are some vagrant plugins required for the installation, user will be prompted to install them if they are not present. Instructions to install the plugins can be extracted from the message.

```text
$ vagrant plugin install <plugin-name>
```

After successfull execution of Vagrant, you can log in to your fresh BigchainDB node.

```text
$ vagrant ssh <instance-name>
```

## Make your first transaction
Once you are inside the BigchainDB node, you can verify that BigchainDB docker/process is running.

Verify BigchainDB process:
```text
$ ps -ef | grep bigchaindb
```

OR

Verify BigchainDB Docker:
```text
$ docker ps | grep bigchaindb
```

BigchainDB python driver is pre-installed in the instance, so you can instantly make transactions and verify the functionality. The `bdb_root_url` can be one of the following:
```text
# BigchainDB is running as a process
bdb_root_url = http://<HOST-IP>:9984

OR

# BigchainDB is running inside a docker container
bdb_root_url = http://<HOST-IP>:<DOCKER-PUBLISHED-HOST-PORT>
```
For more details on *how to make a transaction?* Please refer to [Basic Usage Examples](https://docs.bigchaindb.com/projects/py-driver/en/latest/connect.html).

*Note*: If you want to make transactions remotely, you need to install the `bigchaindb-driver`. For detailed instructions on how to install the driver and make your first transaction. Please refer to [Quickstart/Installation](https://docs.bigchaindb.com/projects/py-driver/en/latest/quickstart.html) of BigchainDB driver.