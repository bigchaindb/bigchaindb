#!/bin/bash

docker build -t bigchaindb/mongodb-monitoring-agent:3.0 .

docker push bigchaindb/mongodb-monitoring-agent:3.0
