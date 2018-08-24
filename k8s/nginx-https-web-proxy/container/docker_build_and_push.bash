#!/bin/bash
# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0


docker build -t bigchaindb/nginx-https-web-proxy:0.12 .

docker push bigchaindb/nginx-https-web-proxy:0.12
