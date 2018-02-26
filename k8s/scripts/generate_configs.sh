#!/usr/bin/env bash
set -euo pipefail

source functions

# base directories for operations
BASE_DIR=$(pwd)

# base variables with default values
MDB_CN="mdb-instance"
BDB_CN="bdb-instance"
MDB_MON_CN="mdb-mon-instance"
INDEX=''
CONFIGURE_CA=''
CONFIGURE_MEMBER=''
CONFIGURE_CLIENT=''

cluster_fqdn="test.bigchaindb.com"
secrete_token="test" 
https_key="https_key"
https_cert_chain_pem="https_cert_chain"

# Tendermint data
tm_seeds='123,4565'
tm_validators='11234,1234'
tm_validators_power='1,2'
tm_genesis_time='1234'
tm_chain_id='12341234'


function show_help(){
cat > /dev/stdout << END
${0} --index INDEX --mdb-name MONGODB_MEMBER_COMMON_NAME
--bdb-name BIGCHAINDB_INSTANCE_COMMON_NAME
--mdb-mon-name MONGODB_MONITORING_INSTNACE_COMMON_NAME [--help]
OPTIONAL ARGS:
--mdb-cn - Common name of MongoDB instance:- default ${MDB_CN}
--bdb-cn - Common name of BigchainDB instance:- default ${BDB_CN}
--mdb-mon-cn - Common name of MongoDB monitoring agent:- default ${MDB_MON_CN}
--dir - Absolute path of base directory:- default ${BASE_DIR}
--help - show help
EXAMPLES
- "Generate Certificates for first node(index=1) in the cluster i.e. MongoDB instance: mdb-instance,"
  "BigchainDB instance: bdb-instance, MongoDB monitoring agent: mdb-mon-instance"
  ./cert_gen.sh --index 1 --mdb-cn mdb-instance --bdb-cn bdb-instance \
  --mdb-mon-cn mdb-mon-instance
END
}


while [[ $# -gt 0 ]]; do
    arg="$1"
    case $arg in
        --index)
            INDEX="$2"
            shift
        ;;
        --mdb-cn)
            MDB_CN="$2"
            shift
        ;;
        --bdb-cn)
            BDB_CN="$2"
            shift
        ;;
        --mdb-mon-cn)
            MDB_MON_CN="$2"
            shift
        ;;
        --dir)
            BASE_DIR="$2"
            shift
        ;;
        --help)
            show_help
            exit 0
        ;;
        *)
            echo "Unknown option: $1"
            exit 1
        ;;
    esac
    shift
done

BASE_CA_DIR="${BASE_DIR}"/bdb-cluster-ca
BASE_MEMBER_CERT_DIR="${BASE_DIR}"/member-cert
BASE_CLIENT_CERT_DIR="${BASE_DIR}"/client-cert
BASE_EASY_RSA_PATH='easy-rsa-3.0.1/easyrsa3'
BASE_K8S_DIR="${BASE_DIR}"/k8s

# sanity checks
if [[ -z "${INDEX}" ]] ; then
    echo "Missing required arguments"
    exit 1
fi

# # Configure Root CA
# mkdir $BASE_CA_DIR
# configure_common $BASE_CA_DIR
# configure_root_ca $BASE_CA_DIR/$BASE_EASY_RSA_PATH


# # Configure Member Request/Key generation
# mkdir $BASE_MEMBER_CERT_DIR
# configure_common $BASE_MEMBER_CERT_DIR
# configure_member_cert_gen $BASE_MEMBER_CERT_DIR/$BASE_EASY_RSA_PATH

# # Configure Client Request/Key generation
# mkdir $BASE_CLIENT_CERT_DIR
# configure_common $BASE_CLIENT_CERT_DIR
# configure_client_cert_gen $BASE_CLIENT_CERT_DIR/$BASE_EASY_RSA_PATH

# import_requests $BASE_CA_DIR/$BASE_EASY_RSA_PATH
# sign_requests $BASE_CA_DIR/$BASE_EASY_RSA_PATH
# make_pem_files $BASE_CA_DIR/$BASE_EASY_RSA_PATH $BASE_K8S_DIR
# convert_b64 $BASE_K8S_DIR $BASE_CA_DIR/$BASE_EASY_RSA_PATH $BASE_CLIENT_CERT_DIR/$BASE_EASY_RSA_PATH

get_users $BASE_K8S_DIR $BASE_CA_DIR/$BASE_EASY_RSA_PATH
generate_secretes_no_threescale $BASE_K8S_DIR $secrete_token $https_key $https_cert_chain_pem

generate_config_map $BASE_K8S_DIR $cluster_fqdn $tm_seeds $tm_validators $tm_validators_power $tm_genesis_time $tm_chain_id
