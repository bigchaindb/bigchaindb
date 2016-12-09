#!/bin/bash

set -e -x

if [ "${TOXENV}" == "py34" ] || [ "${TOXENV}" == "py35" ]; then
    rethinkdb --daemon
fi
