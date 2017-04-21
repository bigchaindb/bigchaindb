#!/bin/bash

docker build -t bigchaindb/mongodb-backup-agent:1.0 .

docker push bigchaindb/mongodb-backup-agent:1.0
