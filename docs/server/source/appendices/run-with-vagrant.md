# Run BigchainDB with Vagrant

**NOT for Production Use**

You can use the following instructions to deploy a single or multi node
BigchainDB setup for dev/test using Vagrant. Vagrant will set up the BigchainDB node(s)
with all the dependencies along with MongoDB and BigchainDB Python driver. You
can also tweak the following configurations for the BigchainDB node(s).
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
- Deploy node with Docker
  - Deploy all the services in Docker containers or as processes.
- Number of BigchainDB nodes
  - If you want to deploy the services inside Docker containers, you
  can specify number of member(s) in the BigchainDB cluster.
- Upstart Script
- Vagrant Provider
  - Virtualbox
  - VMware

## Minimum Requirements | Vagrant
Minimum resource requirements for a single node BigchainDB dev setup. **The more the better**:
- Memory >= 512MB
- VCPUs >= 1

## Install dependencies | Vagrant
1. [VirtualBox](https://www.virtualbox.org/wiki/Downloads) >= 5.0.0
2. [Vagrant](https://www.vagrantup.com/downloads.html) >= 1.16.0

## Clone the BigchainDB repository | Vagrant
```text
$ git clone https://github.com/bigchaindb/bigchaindb.git
```

## Configuration | Vagrant
Navigate to `bigchaindb/pkg/configuration/vars/` inside the BigchainDB repository.
```text
$ cd bigchaindb/pkg/configuration/vars/
```

Edit `bdb-config.yml` as per your requirements. Sample `bdb-config.yml`:

```text
---
deploy_docker: false #[true, false]
docker_cluster_size: 1
upstart: "/bigchaindb/scripts/bootstrap.sh"
bdb_hosts:
  - name: "bdb-node-01"
    box:
      name: "ubuntu/xenial64"
    ram: "2048"
    vcpus: "2"
    network:
      ip: "10.20.30.40"
      type: "private_network"
```

**Note**: You can spawn multiple instances to orchestrate a multi-node BigchainDB cluster.
Here is a sample `bdb-config.yml`:
```text
---
deploy_docker: false #[true, false]
docker_cluster_size: 1
upstart: "/bigchaindb/scripts/bootstrap.sh"
bdb_hosts:
  - name: "bdb-node-01"
    box:
      name: "ubuntu/xenial64"
    ram: "2048"
    vcpus: "2"
    network:
      ip: "10.20.30.40"
      type: "private_network"
  - name: "bdb-node-02"
    box:
      name: "ubuntu/xenial64"
    ram: "2048"
    vcpus: "2"
    network:
      ip: "10.20.30.50"
      type: "private_network"
```
**Note**: You can also orchestrate a multi-node BigchainDB cluster on a single dev host using Docker containers.
Here is a sample `bdb-config.yml`
```text
---
deploy_docker: true #[true, false]
docker_cluster_size: 3
upstart: "/bigchaindb/scripts/bootstrap.sh"
bdb_hosts:
  - name: "bdb-node-01"
    box:
      name: "ubuntu/xenial64"
    ram: "8192"
    vcpus: "4"
    network:
      ip: "10.20.30.40"
      type: "private_network"
```
The above mentioned configuration will deploy a 3 node BigchainDB cluster with Docker containers
on your specified host.

## BigchainDB Setup | Vagrant
To bring up the BigchainDB node(s), run the following command:

```text
$ vagrant up
```

**Note**: There are some vagrant plugins required for the installation,
user will be prompted to install them if they are not present. Instructions
to install the plugins can be extracted from the message.

```text
$ vagrant plugin install <plugin-name>
```

After successfull execution of Vagrant, you can log in to your fresh BigchainDB node.

```text
$ vagrant ssh <instance-name>
```

## Make your first transaction
Once you are inside the BigchainDB node, you can verify that BigchainDB
docker(s)/process(es) is(are) running.

Verify BigchainDB process(es):
```text
$ ps -ef | grep bigchaindb
```

OR

Verify BigchainDB Docker(s):
```text
$ docker ps | grep bigchaindb
```

The BigchainDB Python Driver is pre-installed in the instance,
so you can use it to make transactions
and verify the functionality of your BigchainDB node.
See the [BigchainDB Python Driver documentation](https://docs.bigchaindb.com/projects/py-driver/en/latest/index.html)
for details on how to use it.

Note 1: The `bdb_root_url` can be one of the following:
```text
# BigchainDB is running as a process
bdb_root_url = http://<HOST-IP>:9984

OR

# BigchainDB is running inside a docker container
bdb_root_url = http://<HOST-IP>:<DOCKER-PUBLISHED-HOST-PORT>
```

Note 2: BigchainDB has [other drivers as well](../drivers-clients/index.html).
