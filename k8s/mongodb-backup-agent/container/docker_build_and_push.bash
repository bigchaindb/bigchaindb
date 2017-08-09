#!/bin/bash

docker build -t bigchaindb/mongodb-backup-agent:3.2 .

docker push bigchaindb/mongodb-backup-agent:3.2
