#!/bin/bash

if [ ! -f "$BIGCHAINDB_CONFIG_PATH"  -a ! -d "$BIGCHAINDB_CONFIG_PATH" ]; then
  bigchaindb -y configure
fi

bigchaindb --experimental-start-rethinkdb start
