# Vanshdeep's Notes on Running a Local Dev Node as Processes

The following doc describes how to run a local node for developing BigchainDB Tendermint version.

There are two crucial dependencies required to start a local node:

- MongoDB
- Tendermint

and of course you also need to install BigchainDB Sever from the local code you just developed.


## Installing MongoDB

MongoDB can be easily installed, just refer their [installation documentation](https://docs.mongodb.com/manual/installation/) for your distro. 
We know MongoDB 3.4 works with BigchainDB.
MongoDB 3.6 _might_ work, or it might not. You could try it.
After the installation of MongoDB is complete, run MongoDB using `sudo mongod --replSet=bigchain-rs`


## Installing Tendermint

### Installing Tendermint Using Docker

Tendermint can be run directly using the docker image. Refer [here](https://hub.docker.com/r/tendermint/tendermint/) for more details.


### Installing Tendermint from Source
- Before we can begin installing Tendermint one should ensure that the Golang is installed on system and `$GOPATH` should be set in the `.bashrc` or `.zshrc`. An example setup is shown below

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

- Now we can install Glide which is vendor package manger for Golang,

```bash
$ go get github.com/Masterminds/glide

...
...

$ glide -h
NAME:
   glide - Vendor Package Management for your Go projects.

   Each project should have a 'glide.yaml' file in the project directory. Files
   look something like this:

...
```

- Now we install Tendermint from source,

```bash
$ mkdir -p $GOPATH/src/github.com/tendermint && cd $_
$ git clone https://github.com/tendermint/tendermint
...
$ cd tendermint && glide install
$ go install ./cmd/tendermint
```

- If the above commands were executed successfully then Tendermint is installed at `$GOPATH/bin`. To ensure Tendermint's installed fine execute the following command,

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

## Installing BigchainDB

To install BigchainDB from source (for dev), clone the repo and execute the following command, (it is better that you create a virtual env for this)

```bash
$ git clone https://github.com/bigchaindb/bigchaindb.git
...
$ git checkout tendermint
$ pip install -e .[dev]  #  or  pip install -e '.[dev]'  # for zsh
```


## Running All Tests

To execute tests when developing a feature or fixing a bug one could use the following command,

```bash
$ pytest -v --database-backend=localmongodb
```

NOTE: MongoDB and Tendermint should be running as discussed above.

One could mark a specific test and execute the same by appending `-m my_mark` to the above command.

Although the above should prove sufficient in most cases but in case tests are failing on Travis CI then the following command can be used to possibly replicate the failure locally,

```bash
$ docker-compose run --rm --no-deps bdb pytest -v --cov=bigchaindb
```

NOTE: before executing the above command the user must ensure that they reset the Tendermint container by executing `tendermint usafe_reset_all` command in the Tendermint container.


### Closing Notes

How to check `bigchaindb upsert-validator`:

- Clean bigchaindb (`bigchaindb drop`, `bigchaindb init`) and execute `bigchaindb upsert-validator B0E42D2589A455EAD339A035D6CE1C8C3E25863F268120AA0162AD7D003A4014 10`
- Start Tendermint
 - `tendermint init`
 - `tendermint unsafe_reset_all`
 - `tendermint node --consensus.create_empty_blocks=false`
- Start BigchainDB with `bichaindb start`
- Execute `curl http://localhost:46657/validators`

