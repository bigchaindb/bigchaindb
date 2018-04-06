#!/bin/bash

docker build -t bigchaindb/mongodb-monitoring-agent:2.0.0-alpha .

docker push bigchaindb/mongodb-monitoring-agent:2.0.0-alpha
