#!/bin/bash

set -e -x

if [[ -z ${TOXENV} ]]; then

  if [[ ${BIGCHAINDB_CI_ABCI} == 'enable' ]]; then
      docker-compose up -d bigchaindb
  else
      docker-compose up -d bdb
  fi

fi
