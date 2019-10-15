<!---
Copyright BigchainDB GmbH and BigchainDB contributors
SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
Code is Apache-2.0 and docs are CC-BY-4.0
--->

# Set Up BigchainDB, MongoDB and Tendermint

We now install and configure software that must run
in every BigchainDB node: BigchainDB Server,
MongoDB and Tendermint.

## Install BigchainDB Server

BigchainDB Server requires **Python 3.6+**, so make sure your system has it.

Install the required OS-level packages:

```
# For Ubuntu 18.04:
sudo apt install -y python3-pip libssl-dev
# Ubuntu 16.04, and other Linux distros, may require other packages or more packages
```

BigchainDB Server requires [gevent](http://www.gevent.org/), and to install gevent, you must use pip 19 or later (as of 2019, because gevent now uses manylinux2010 wheels). Upgrade pip to the latest version:

```
sudo pip3 install -U pip
```

Now install the latest version of BigchainDB Server.
You can find the latest version by going
to the [BigchainDB project release history page on PyPI](https://pypi.org/project/BigchainDB/#history).
For example, to install version 2.0.0, you would do:

```
# Change 2.0.0 to the latest version as explained above:
sudo pip3 install bigchaindb==2.0.0
```

Check that you installed the correct version of BigchainDB Server using `bigchaindb --version`.

## Configure BigchainDB Server

To configure BigchainDB Server, run:

```
bigchaindb configure
```

The first question is ``API Server bind? (default `localhost:9984`)``.

* If you're using NGINX (e.g. if you want HTTPS),
  then accept the default value (`localhost:9984`).
* If you're not using NGINX, then enter the value `0.0.0.0:9984`

You can accept the default value for all other BigchainDB config settings.

If you're using NGINX, then you should edit your BigchainDB config file
(in `$HOME/.bigchaindb` by default) and set the following values
under `"wsserver"`:

```
"advertised_scheme": "wss",
"advertised_host": "bnode.example.com",
"advertised_port": 443
```

where `bnode.example.com` should be replaced by your node's actual subdomain.

## Install (and Start) MongoDB

Install a recent version of MongoDB.
BigchainDB Server requires version 3.4 or newer.

```
sudo apt install mongodb
```

If you install MongoDB using the above command (which installs the `mongodb` package),
it also configures MongoDB, starts MongoDB (in the background),
and installs a MongoDB startup script
(so that MongoDB will be started automatically when the machine is restarted).

Note: The `mongodb` package is _not_ the official MongoDB package
from MongoDB the company. If you want to install the official MongoDB package,
please see
[the MongoDB documentation](https://docs.mongodb.com/manual/installation/).
Note that installing the official package _doesn't_ also start MongoDB.

## Install Tendermint

The version of BigchainDB Server described in these docs only works well
with Tendermint 0.31.5 (not a higher version number). Install that:

```
sudo apt install -y unzip
wget https://github.com/tendermint/tendermint/releases/download/v0.31.5/tendermint_v0.31.5_linux_amd64.zip
unzip tendermint_v0.31.5_linux_amd64.zip
rm tendermint_v0.31.5_linux_amd64.zip
sudo mv tendermint /usr/local/bin
```

## Start Configuring Tendermint

You won't be able to finish configuring Tendermint until you have some information
from the other nodes in the network, but you can start by doing:

```
tendermint init
```
