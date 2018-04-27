#!/bin/bash

docker build -t bigchaindb/tendermint:2.0.0-alpha3 .

docker push bigchaindb/tendermint:2.0.0-alpha3
