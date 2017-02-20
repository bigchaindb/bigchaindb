# Quickstart

This page has instructions to set up a single stand-alone BigchainDB node for learning or experimenting. Instructions for other cases are [elsewhere](introduction.html). We will assume you're using Ubuntu 16.04 or similar. If you're not using Linux, then you might try [running BigchainDB with Docker](appendices/run-with-docker.html).

A. Install the database backend. 

[Install RethinkDB Server](https://rethinkdb.com/docs/install/ubuntu/) or
[Install MongoDB Server 3.4+](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/)

B. Run the database backend. Open a Terminal and run the command:

with RethinkDB
```text
$ rethinkdb
```

with MongoDB __3.4+__
```text
$ mongod --replSet=bigchain-rs
```

C. Ubuntu 16.04 already has Python 3.5, so you don't need to install it, but you do need to install some other things:
```text
$ sudo apt-get update
$ sudo apt-get install g++ python3-dev libffi-dev
```

D. Get the latest version of pip and setuptools:
```text
$ sudo apt-get install python3-pip
$ sudo pip3 install --upgrade pip setuptools
```

E. Install the `bigchaindb` Python package from PyPI:
```text
$ sudo pip3 install bigchaindb
```

F. Configure the BigchainDB Server: and run BigchainDB Server:

with RethinkDB
```text
$ bigchaindb -y configure rethinkdb
```

with MongoDB
```text
$ bigchaindb -y configure mongodb
```

G. Run the BigchainDB Server:
```text
$ bigchaindb start
```

That's it!

Next Steps: You could... 

* [install the BigchainDB Python Driver](https://docs.bigchaindb.com/projects/py-driver/en/latest/quickstart.html) and
* [use the BigchainDB Python Driver to build a valid transaction, and post that transaction to your running server](https://docs.bigchaindb.com/projects/py-driver/en/latest/usage.html).

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
