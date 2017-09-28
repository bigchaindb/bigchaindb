#!/bin/bash

docker build -t bigchaindb/mongodb-backup-agent:3.5 .

docker push bigchaindb/mongodb-backup-agent:3.5
