#!/bin/bash

set -e -x

if [[ -z ${TOXENV} ]]; then
    codecov -v
fi
