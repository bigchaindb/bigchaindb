# Quickstart

This page has instructions to set up a single stand-alone BigchainDB node for learning or experimenting. Instructions for other cases are [elsewhere](introduction.html). We will assume you're using Ubuntu 16.04 or similar. You may prefer to try [running BigchainDB with Docker](appendices/run-with-docker.html) instead.

Update apt's list of packages, then install some packages:
```text
$ sudo apt-get update
$ sudo apt-get install curl unzip libffi-dev libssl-dev python3-pip
```

Install Tendermint. Note: The following commands are for Tendermint 0.12.1. To determine the latest version, see [https://tendermint.com/downloads](https://tendermint.com/downloads).
```text
$ curl -fOL# https://s3-us-west-2.amazonaws.com/tendermint/binaries/tendermint/v0.12.1/tendermint_0.12.1_linux_amd64.zip
$ unzip tendermint_0.12.1_linux_amd64.zip
$ sudo mv tendermint /usr/local/bin
$ rm tendermint_0.12.1_linux_amd64.zip
```

Configure Tendermint:
```text
$ tendermint init
```

Install MongoDB:

🖝 [Install MongoDB Server 3.4+](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/).

Create the default database directory for MongoDB, i.e. /data/db:
```text
$ sudo mkdir -p /data/db
```

Give the user read/write/execute permissions on /data/db:
```text
$ sudo chmod -R 700 /data/db
```

Get the latest version of pip and setuptools:
```text
$ sudo pip3 install --upgrade pip setuptools
```

Install the `bigchaindb` Python package from PyPI:
```text
$ sudo pip3 install bigchaindb
```

Configure BigchainDB Server:
```text
$ bigchaindb -y configure mongodb
```

Set some environment variables:
```text
$ export BIGCHAINDB_START_TENDERMINT=0
$ export TENDERMINT_HOST=localhost
$ export TENDERMINT_PORT=46657
```

Run MongoDB:
```text
$ sudo mongod --replSet=bigchain-rs
```

That will take hold of that terminal, so open a new terminal and continue.

Run BigchainDB Server:
```text
$ bigchaindb start
```

Verify BigchainDB Server setup by visiting the BigchainDB Root URL in your browser:

[http://127.0.0.1:9984/](http://127.0.0.1:9984/)

The response should be a JSON object with information about the API endpoints, docs URL and more.

In yet another terminal, run Tendermint:
```text
$ tendermint unsafe_reset_all
$ tendermint node
```

You now have a running BigchainDB Node and can post transactions to it.
One way to do that is to use the BigchainDB Python Driver.

[Install the BigchainDB Python Driver (link)](https://docs.bigchaindb.com/projects/py-driver/en/latest/quickstart.html)

<hr>

<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
