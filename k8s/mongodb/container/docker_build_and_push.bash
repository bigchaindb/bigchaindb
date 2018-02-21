#!/bin/bash

docker build -t bigchaindb/localmongodb:unstable .
docker push bigchaindb/localmongodb:unstable
