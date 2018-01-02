#!/bin/bash

docker build -t bigchaindb/tendermint:unstable-tmt .

docker push bigchaindb/tendermint:unstable-tmt
