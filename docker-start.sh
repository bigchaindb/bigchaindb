#!/bin/bash

while ! timeout 1 bash -c "cat < /dev/null > /dev/tcp/$BIGCHAINDB_DATABASE_HOST/28015"; do sleep 1; done
sleep 5

if [ ! -f "$BIGCHAINDB_CONFIG_PATH"  -a ! -d "$BIGCHAINDB_CONFIG_PATH" ]; then
  bigchaindb -y configure
fi

bigchaindb start
