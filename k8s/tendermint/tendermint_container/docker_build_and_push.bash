#!/bin/bash

docker build -t bigchaindb/tendermint:2.0.0-alpha .

docker push bigchaindb/tendermint:2.0.0-alpha
