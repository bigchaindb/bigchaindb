#!/bin/bash
# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0


# MongoDB configuration
[ "$(stat -c %U /data/db)" = mongodb ] || chown -R mongodb /data/db

# BigchainDB configuration
bigchaindb-monit-config

nohup mongod --bind_ip_all > "$HOME/.bigchaindb-monit/logs/mongodb_log_$(date +%Y%m%d_%H%M%S)" 2>&1 &

# Tendermint configuration
tendermint init

monit -d 5 -I -B
