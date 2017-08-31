#!/bin/bash

docker build -t bigchaindb/mongodb-monitoring-agent:3.1 .

docker push bigchaindb/mongodb-monitoring-agent:3.1
