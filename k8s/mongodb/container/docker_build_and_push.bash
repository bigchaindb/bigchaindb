#!/bin/bash

docker build -t bigchaindb/localmongodb:1.0 .
docker push bigchaindb/localmongodb:1.0
