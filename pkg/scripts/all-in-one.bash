#!/bin/bash

# MongoDB configuration
[ "$(stat -c %U /data/db)" = mongodb ] || chown -R mongodb /data/db

# BigchainDB configuration
bigchaindb-monit-config

nohup mongod > "$HOME/.bigchaindb-monit/logs/mongodb_log_$(date +%Y%m%d_%H%M%S)" 2>&1 &

# Tendermint configuration
tendermint init

monit -d 5 -I -B
