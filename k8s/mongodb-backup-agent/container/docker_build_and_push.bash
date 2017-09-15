#!/bin/bash

docker build -t bigchaindb/mongodb-backup-agent:3.4 .

docker push bigchaindb/mongodb-backup-agent:3.4
