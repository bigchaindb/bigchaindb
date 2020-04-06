#!/bin/bash
# Copyright © 2020 Interplanetary Database Association e.V.,
# BigchainDB and IPDB software contributors.
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0


docker build -t bigchaindb/nginx_pub_key_access:2.0.0-alpha3 .

docker push bigchaindb/nginx_pub_key_access:2.0.0-alpha3
