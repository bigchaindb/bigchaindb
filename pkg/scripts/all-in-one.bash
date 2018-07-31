#!/bin/bash

# MongoDB configuration
[ "$(stat -c %U /data/db)" = mongodb ] || chown -R mongodb /data/db
nohup mongod > /tmp/mongodb_log_$(date +%Y%m%d_%H%M%S) 2>&1 &

# Tendermint configuration
tendermint init

# BigchainDB configuration
bigchaindb-monit-config
monit -d 5 -I -B
