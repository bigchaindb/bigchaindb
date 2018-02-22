#!/bin/bash

docker build -t bigchaindb/tendermint:unstable .

docker push bigchaindb/tendermint:unstable
