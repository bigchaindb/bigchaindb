#!/bin/bash

docker build -t bigchaindb/mongodb-backup-agent:3.1 .

docker push bigchaindb/mongodb-backup-agent:3.1
