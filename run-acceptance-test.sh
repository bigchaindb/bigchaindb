#!/usr/bin/env bash

# Set up a BigchainDB node and return only when we are able to connect to both
# the BigchainDB container *and* the Tendermint container.
setup () {
	docker-compose up -d bigchaindb

	# Try to connect to the containers for maximum three times, and wait
	# one second between tries.
	for i in $(seq 3); do
		if $(docker-compose run --rm curl-client); then
			break
		else
			sleep 1
		fi
	done
}

run_test () {
	docker-compose run --rm python-acceptance pytest /src
}

teardown () {
	docker-compose down
}

setup
run_test
exitcode=$?
teardown

exit $exitcode
