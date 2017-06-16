#!/bin/bash

docker build -t bigchaindb/mongodb-backup-agent:3.0 .

docker push bigchaindb/mongodb-backup-agent:3.0
