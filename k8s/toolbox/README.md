<!---
Copyright BigchainDB GmbH and BigchainDB contributors
SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
Code is Apache-2.0 and docs are CC-BY-4.0
--->

## Docker container with debugging tools

*  curl
*  bind-utils - provides nslookup, dig
*  python3
*  make

## Build

`docker build -t bigchaindb/toolbox .`

## Push

`docker push bigchaindb/toolbox`
