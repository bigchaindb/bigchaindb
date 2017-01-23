# Quickstart

This page has instructions to set up a single stand-alone BigchainDB node for learning or experimenting. Instructions for other cases are [elsewhere](introduction.html). We will assume you're using Ubuntu 16.04 or similar. If you're not using Linux, then you might try [running BigchainDB with Docker](appendices/run-with-docker.html).

A. [Install RethinkDB Server](https://rethinkdb.com/docs/install/ubuntu/)

B. Open a Terminal and run RethinkDB Server with the command:
```text
rethinkdb
```

C. Ubuntu 16.04 already has Python 3.5, so you don't need to install it, but you do need to install some other things:
```text
sudo apt-get update
sudo apt-get install g++ python3-dev libffi-dev
```

D. Get the latest version of pip and setuptools:
```text
sudo apt-get install python3-pip
sudo pip3 install --upgrade pip setuptools
```

E. Install the `bigchaindb` Python package from PyPI:
```text
sudo pip3 install bigchaindb
```

F. Configure and run BigchainDB Server:
```text
bigchaindb -y configure
bigchaindb start
```

That's it!

Next Steps: You could build valid transactions and push them to your running BigchainDB Server using the [BigchaindB Python Driver](https://docs.bigchaindb.com/projects/py-driver/en/latest/index.html).
