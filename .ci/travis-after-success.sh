#!/bin/bash

set -e -x

if [ "${TOXENV}" == "py35" ]; then
    codecov
fi
