#!/bin/bash
# Rubilink-Blockchain © 2023 Interplanetary Database Association e.V.,
# Rubilink-Blockchain and IPDB software contributors.
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0


docker build -t bigchaindb/tendermint:2.2.2 .

docker push bigchaindb/tendermint:2.2.2
