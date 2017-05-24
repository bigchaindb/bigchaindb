#!/bin/bash

docker build -t bigchaindb/mongodb-monitoring-agent:2.0 .

docker push bigchaindb/mongodb-monitoring-agent:2.0
