#!/bin/bash

docker build -t bigchaindb/mongodb-backup-agent:2.0 .

docker push bigchaindb/mongodb-backup-agent:2.0
