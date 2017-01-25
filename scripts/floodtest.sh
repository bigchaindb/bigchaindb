#!/bin/bash

# testflood.sh
#
# Run BigchainDB test suite repeatedly in parallel. For hunting race conditions.
# 
# Author: scott@bigchaindb.com

set -e

function runWorker () {
	set -x
	if [ ! -d $1 ]
	then
		git clone bigchaindb $1
	fi
	cd $1
	docker-compose -p flood-$1 up -d mdb
	docker-compose -p flood-$1 run --rm bdb-mdb pytest -v -x -s
	# Neccesary so that no root-owned files are left lying around,
	# otherwise we can't clean up outside the container without `sudo`. 
	docker-compose -p flood-$1 run -w/usr/src --rm bdb-mdb bash -c \
		'self=`stat -c %u app/bigchaindb`; chown -R $self:$self app'
	docker-compose stop bdb-mdb
	cd ..
	rm -rf $1
	set +x
	echo "All done."
}


if [ "$1" -eq 0 -o "$1" -ne 0 ] >/dev/null 2>&1; then
	processes=$1
else
	>&2 echo "Usage: $0 [number-of-workers]"
	exit 1
fi

while true; do
	FAIL=0
	for i in $(seq 1 $processes); do
                worker=`printf "worker_%02d\n" $i`
		echo "Launching $worker"
                runWorker $worker &> $worker.log &
	done
	echo "Waiting for workers to finish"
	for job in `jobs -p`; do
		wait $job || let "FAIL+=1"
	done
	if [ "$FAIL" != "0" ]; then
		echo "Runners failed: $FAIL"
		break
	fi
	echo "All workers completed successfully"
	break
done
