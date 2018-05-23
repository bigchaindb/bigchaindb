# How to setup a BigchainDB Network
The process to create a network is both *social* and *technical*: *social* because someone (that we will call **Coordinator**) needs to find at least three other **Members** willing to join the network, and coordinate the effort; *technical* because each member of the network needs to set up a machine running BigchainDB. (Note: a Coordinator is a Member as well.)

A **BigchainDB Network** (*Network* henceforth) is a set of **4 or more BigchainDB Nodes** (*Node* henceforth). Every Node is independently managed by a Member, and runs an instance of the [BigchainDB Server software][bdb:software]. At the **Genesis** of a Network, there **MUST** be at least **4** Nodes ready to connect. After the Genesis, a Network can dynamically add new Nodes or remove old Nodes.

A Network will stop working if more than one third of the Nodes are down. The bigger a Network, the more failures it can handle. A Network of size 4 can tolerate only 1 failure, so if 3 out of 4 Nodes are online, everything will work as expected. Eventually, the Node that was offline will automatically sync with the others.


## Before we start
This tutorial assumes you have basic knowledge on how to manage a GNU/Linux machine. The commands are tailored for an up-to-date *Debian-like* distribution (we use an **Ubuntu 18.04 LTS** Virtual Machine on Microsoft Azure): if you are on a different distribution you might need to adapt the names of the packages installed.

We don't make any assumptions on **where** you run the Node.
You can run the BigchainDB Server on a Virtual Machine on the cloud, on a machine in your data center, on a Raspberry Pi. Just make sure that your Node is reachable by the other Nodes, a **non-exhaustive list of examples**:
- **good**: all Nodes running in the cloud using public IPs.
- **bad**: some Nodes running in the cloud using public IPs, some Nodes in a private network.
- **good**: all Nodes running in a private network.

The rule of thumb is: if Nodes can ping each other, then you are good to go.

The next sections are labelled with **Member** or **Coordinator**, depending on who should follow the instructions. Remember, a Coordinator is also a Member.

## Member: Set up a Node
Every Member in the Network **must** set up its own Node. The process consists of installing three components, BigchainDB Server, Tendermint Core, and MongoDB, and configure the firewall.

**Important note on security: it's up to the Member to harden their system.**

### Install the required software
Make sure your system is up to date.

```
sudo apt update
sudo apt full-upgrade
```

#### Install BigchainDB Server
BigchainDB Server requires **Python 3.6+**, make sure your system has it. Install the required packages:

```
sudo apt install -y python3-pip libssl-dev
```

Now install the latest version of BigchainDB. Check the [project page on PyPI][bdb:pypi] for the last version (`2.0.0a6` at the time of writing) and install it:

```
sudo pip3 install bigchaindb==2.0.0a6
```

Check you installed the correct version of BigchainDB Server with `bigchaindb --version`.

#### Install MongoDB
Install a recent version of MongoDB. BigchainDB Server requires `3.4` or newer.

```
sudo apt install mongodb
```

The package manager should take care of installing the startup script for MongoDB as well.

#### Install Tendermint
Install a [recent version of Tendermint][tendermint:releases]. BigchainDB Server requires `0.19` or newer.

```
sudo apt install -y unzip
wget https://github.com/tendermint/tendermint/releases/download/v0.19.3/tendermint_0.19.3_linux_amd64.zip
unzip tendermint_0.19.3_linux_amd64.zip
rm tendermint_0.19.3_linux_amd64.zip
sudo mv tendermint /usr/local/bin
```

### Firewall settings
Make sure to accept inbound connections to (`22`, you don't want to lock you out), `9984`, `9985`, and `46656`.

```
sudo ufw allow 22/tcp
sudo ufw allow 9984/tcp
sudo ufw allow 9985/tcp
sudo ufw allow 46656/tcp
sudo ufw enable
```

Some cloud providers, like Microsoft Azure, require you to go through their portal to allow inbound connections on custom ports.

## Member: Configure BigchainDB Server
To configure BigchainDB Server, run:

```
bigchaindb configure
```

The first question is ``API Server bind? (default `localhost:9984`)``, to expose the API to the public, bind the API Server to `0.0.0.0:9984`. Unless you have specific needs, you can keep the default value for all other questions.

## Member: Generate the private key and node id
A Node is identified by the triplet `<hostname, node_id, public_key>`.

As a Member, it's your duty to create and store securely your private key, and share your `hostname`, `node_id`, and `public_key` with the other members of the network.

To generate all of that, run:

```
tendermint init
```

The `public_key` is stored in the file `.tendermint/config/priv_validator.json`, and it should look like:

```json
{
  "address": "5943A9EF6285791A504918E1D117BC7F6A615C98",
  "pub_key": {
    "type": "AC26791624DE60",
    "value": "W3tqeMCU3d4SHDKqrwQWTahTW/wpieIAKZQxUxLv6rI="
  },
  "last_height": 0,
  "last_round": 0,
  "last_step": 0,
  "priv_key": {
    "type": "954568A3288910",
    "value": "3sv9aExgME6MMjx0JoKVy7KtED8PBiPcyAgsYmVizslbe2p4wJTd3hIcMqqvBBZNqFNb/CmJ4gAplDFTEu/qsg=="
  }
}
```

To extract your `node_id`, run the command:

```
tendermint show_node_id
```

Share with all other Members your `node_id`, `pub_key.value`, and the host name or IP of your Node.

**Important note on security: each Member should take extra steps to verify the public keys they receive from the other Members have not been tampered, e.g. a key signing party would help address that.**


## Coordinator: Initialize the Network
At this point the Coordinator should have received the data from all the Members, and should combine them in the `.tendermint/config/genesis.json` file:

```json
{
  "genesis_time": "0001-01-01T00:00:00Z",
  "chain_id": "test-chain-la6HSr",
  "validators": [
    {
      "pub_key": {
        "type": "AC26791624DE60",
        "value": "<Member 1 public key>"
      },
      "power": 10,
      "name": "<Member 1 name>"
    },
    {
      "pub_key": {
        "type": "AC26791624DE60",
        "value": "<Member 2 public key>"
      },
      "power": 10,
      "name": "<Member 2 name>"
     },
     {
       "...": { },
     },
     {
       "pub_key": {
         "type": "AC26791624DE60",
         "value": "<Member N public key>"
       },
       "power": 10,
       "name": "<Member N name>"
     }
  ],
  "app_hash": ""
}
```

The new `genesis.json` file contains the data that describes the Network. The key `name` is the Member's moniker, it can be any valid string, put something human readable like: "Alice's Node Shop".

At this point, the Coordinator must share the new `genesis.json` file with all Members.

## Member: Connect to the other Members
At this point the Member should have received the `genesis.json` file.

**Important note on security: each Member should verify that the `genesis.json` file contains the correct public keys.**

The Member must copy the `genesis.json` file in the local `.tendermint/config` directory. Every Member now shares the same `chain_id`, `genesis_time`, used to identify the Network, and the same list of `validators`.

The Member must edit the `.tendermint/config/config.toml` file and make the following changes:

```
...

create_empty_blocks = false
...

persistent_peers = "<Member 1 node id>@<Member 1 hostname>:46656,\
<Member 2 node id>@<Member 2 hostname>:46656,\
<Member N node id>@<Member N hostname>:46656,"
```

Now the Member must run two commands:
- `bigchaindb start`
- `tendermint node`

The commands will run on the foreground, you might want to use `nohup`, `tmux`, or `screen` to keep them running after you logout. The recommended approach is to create startup scripts for both BigchainDB and Tendermint, so they will start right after the boot of the operating system.


## Member: Dynamically add a new Member to the Network
TBD.


[bdb:software]: https://github.com/bigchaindb/bigchaindb/
[bdb:pypi]: https://pypi.org/project/BigchainDB/#history
[tendermint:releases]: https://github.com/tendermint/tendermint/releases
