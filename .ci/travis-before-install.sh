#!/bin/bash

if [[ -z ${TOXENV} ]]; then
  sudo apt-get update
  sudo apt-get -y -o Dpkg::Options::="--force-confnew" install docker-ce

  sudo rm /usr/local/bin/docker-compose
  curl -L https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-`uname -s`-`uname -m` > docker-compose
  chmod +x docker-compose
  sudo mv docker-compose /usr/local/bin
fi
