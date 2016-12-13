#!/bin/bash

set -e -x

pip install --upgrade pip

if [[ -n ${TOXENV} ]]; then
    pip install --upgrade tox
else
    pip install -e .[test]
    pip install --upgrade codecov
fi
