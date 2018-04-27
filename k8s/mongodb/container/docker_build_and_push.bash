#!/bin/bash

docker build -t bigchaindb/localmongodb:2.0.0-alpha3 .
docker push bigchaindb/localmongodb:2.0.0-alpha3
