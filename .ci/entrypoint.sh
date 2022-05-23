#!/bin/bash
# Copyright © 2020 Interplanetary Database Association e.V.,
# BigchainDB and IPDB software contributors.
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0


set -e -x

if [[ ${BIGCHAINDB_CI_ABCI} == 'enable' ]]; then
    sleep 3600
else
    bigchaindb -l DEBUG start
fi
