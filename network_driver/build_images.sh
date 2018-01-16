#!/bin/bash

# build mongodb image
docker build -t mongodb:bdb -f Dockerfile.mongo .

# build mongodb image
docker build -t tendermint:bdb -f Dockerfile.tendermint .

# build bigchaindb image
docker build -t bigchaindb:itest -f ../Dockerfile.itest .
