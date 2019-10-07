<!---
Copyright BigchainDB GmbH and BigchainDB contributors
SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
Code is Apache-2.0 and docs are CC-BY-4.0
--->

# Notes on Running a Local Dev Node as Processes

The following doc describes how to run a local node for developing BigchainDB Tendermint version.

There are two crucial dependencies required to start a local node:

- MongoDB
- Tendermint

and of course you also need to install BigchainDB Sever from the local code you just developed.

## Install and Run MongoDB

MongoDB can be easily installed, just refer to their [installation documentation](https://docs.mongodb.com/manual/installation/) for your distro.
We know MongoDB 3.4 and 3.6 work with BigchainDB.
After the installation of MongoDB is complete, run MongoDB using `sudo mongod`

## Install and Run Tendermint

### Installing a Tendermint Executable

The version of BigchainDB Server described in these docs only works well with Tendermint 0.31.5 (not a higher version number). Install that:

```bash
$ sudo apt install -y unzip
$ wget https://github.com/tendermint/tendermint/releases/download/v0.31.5/tendermint_v0.31.5_linux_amd64.zip
$ unzip tendermint_v0.31.5_linux_amd64.zip
$ rm tendermint_v0.31.5_linux_amd64.zip
$ sudo mv tendermint /usr/local/bin
```

### Installing Tendermint Using Docker

Tendermint can be run directly using the docker image. Refer [here](https://hub.docker.com/r/tendermint/tendermint/) for more details.

### Installing Tendermint from Source

Before we can begin installing Tendermint one should ensure that the Golang is installed on system and `$GOPATH` should be set in the `.bashrc` or `.zshrc`. An example setup is shown below

```bash

$ echo $GOPATH
/home/user/Documents/go
$ go -h
Go is a tool for managing Go source code.

Usage:

	go command [arguments]

The commands are:

	build       compile packages and dependencies
	clean       remove object files

...

```

- We can drop `GOPATH` in `PATH` so that installed Golang packages are directly available in the shell. To do that add the following to your `.bashrc`

```bash
export PATH=${PATH}:${GOPATH}/bin
```

Follow [the Tendermint docs](https://tendermint.com/docs/introduction/install.html#from-source) to install Tendermint from source.

If the installation is successful then Tendermint is installed at `$GOPATH/bin`. To ensure Tendermint's installed fine execute the following command,

```bash
$ tendermint -h
Tendermint Core (BFT Consensus) in Go

Usage:
  tendermint [command]

Available Commands:
  gen_validator               Generate new validator keypair
  help                        Help about any command
  init                        Initialize Tendermint
...

```

### Running Tendermint

- We can initialize and run tendermint as follows,
```bash
$ tendermint init
...

$ tendermint node --consensus.create_empty_blocks=false
```
The argument `--consensus.create_empty_blocks=false` specifies that Tendermint should not commit empty blocks.


- To reset all the data stored in Tendermint execute the following command,

```bash
$ tendermint unsafe_reset_all
```

## Install BigchainDB

To install BigchainDB from source (for dev), clone the repo and execute the following command, (it is better that you create a virtual env for this)

```bash
$ git clone https://github.com/bigchaindb/bigchaindb.git
$ cd bigchaindb
$ pip install -e .[dev]  #  or  pip install -e '.[dev]'  # for zsh
```

## Running All Tests

To execute tests when developing a feature or fixing a bug one could use the following command,

```bash
$ pytest -v
```

NOTE: MongoDB and Tendermint should be running as discussed above.

One could mark a specific test and execute the same by appending `-m my_mark` to the above command.

Although the above should prove sufficient in most cases but in case tests are failing on Travis CI then the following command can be used to possibly replicate the failure locally,

```bash
$ docker-compose run --rm --no-deps bdb pytest -v --cov=bigchaindb
```

NOTE: before executing the above command the user must ensure that they reset the Tendermint container by executing `tendermint usafe_reset_all` command in the Tendermint container.
