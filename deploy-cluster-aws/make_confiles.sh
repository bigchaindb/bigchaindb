#! /bin/bash

# The set -e option instructs bash to immediately exit
# if any command has a non-zero exit status
set -e

function printErr()
    {
        echo "usage: ./make_confiles.sh <dir> <number_of_files>"
        echo "No argument $1 supplied"
    }

if [ -z "$1" ]; then
    printErr "<dir>"
    exit 1
fi

if [ -z "$2" ]; then
    printErr "<number_of_files>"
    exit 1
fi

CONFDIR=$1
NUMFILES=$2

# If $CONFDIR exists, remove it
if [ -d "$CONFDIR" ]; then
    rm -rf $CONFDIR
fi

# Create $CONFDIR
mkdir $CONFDIR

# Use the bigchaindb configure command to create
# $NUMFILES BigchainDB config files in $CONFDIR
for (( i=0; i<$NUMFILES; i++ )); do
    CONPATH=$CONFDIR"/bcdb_conf"$i
    echo "Writing "$CONPATH
    bigchaindb -y -c $CONPATH configure
done
