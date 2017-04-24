#!/bin/bash

docker build -t bigchaindb/mongodb-monitoring-agent:1.0 .

docker push bigchaindb/mongodb-monitoring-agent:1.0
