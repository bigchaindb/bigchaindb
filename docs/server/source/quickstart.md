# Quickstart

This page has instructions to set up a single stand-alone BigchainDB node for learning or experimenting. Instructions for other cases are [elsewhere](introduction.html). We will assume you're using Ubuntu 16.04 or similar. If you're not using Linux, then you might try [running BigchainDB with Docker](appendices/run-with-docker.html).

A. Install MongoDB as the database backend. (There are other options but you can ignore them for now.)

[Install MongoDB Server 3.4+](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/)

B. To run MongoDB with default database path i.e. /data/db, open a Terminal and run the following command:
```text
$ sudo mkdir -p /data/db
```

C. Assign rwx(read/write/execute) permissions to the user for default database directory:
```text
$ sudo chmod -R 700 /data/db
```

D. Run MongoDB (but do not close this terminal):
```text
$ sudo mongod --replSet=bigchain-rs
```

E. Ubuntu 16.04 already has Python 3.5, so you don't need to install it, but you do need to install some other things within a new terminal:
```text
$ sudo apt-get update
$ sudo apt-get install libffi-dev libssl-dev
```

F. Get the latest version of pip and setuptools:
```text
$ sudo apt-get install python3-pip
$ sudo pip3 install --upgrade pip setuptools
```

G. Install the `bigchaindb` Python package from PyPI:
```text
$ sudo pip3 install bigchaindb
```

In case you are having problems with installation or package/module versioning, please upgrade the relevant packages on your host by running one the following commands:
```text
$ sudo pip3 install [packageName]==[packageVersion]

OR

$ sudo pip3 install [packageName] --upgrade
```

H. Configure BigchainDB Server:
```text
$ bigchaindb -y configure mongodb
```

I. Run BigchainDB Server:
```text
$ bigchaindb start --init
```

J. Verify BigchainDB Server setup by visiting the BigchainDB Root URL in your browser:

[http://127.0.0.1:9984/](http://127.0.0.1:9984/)

A correctly installed installation will show you a JSON object with information about the API, docs, version and your public key.

You now have a running BigchainDB Server and can post transactions to it.
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
