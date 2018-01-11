#!/bin/bash

docker build -t bigchaindb/mongodb:3.2 .

docker push bigchaindb/mongodb:3.2

# For Tendermint

# docker build -t bigchaindb/mongodb:unstable-tmt . -f Dockerfile-TMT
# docker push bigchaindb/mongodb:unstable-tmt
