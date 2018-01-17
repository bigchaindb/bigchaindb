#!/bin/bash

# build mongodb image
docker build -t mongodb:bdb-itest -f Dockerfile.mongo .

# build mongodb image
docker build -t tendermint:bdb-itest -f Dockerfile.tendermint .

# build bigchaindb image (execute in parent directory)
cd .. && docker build -t bigchaindb:bdb-itest -f Dockerfile.itest .
