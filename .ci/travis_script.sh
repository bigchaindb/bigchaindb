#!/bin/bash

set -e -x

if [[ -n ${TOXENV} ]]; then
  tox -e ${TOXENV}
else
  pytest -v -n auto --cov=bigchaindb
fi
