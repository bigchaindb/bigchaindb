#!/usr/bin/env bash
set -euo pipefail

source vars
source functions

# Default directory for certificates
CERT_DIR="certificates"

# base variables with default values
MDB_CN="mdb-instance"
BDB_CN="bdb-instance"
MDB_MON_CN="mdb-mon-instance"
INDEX='0'
CONFIGURE_CA='true'
CONFIGURE_MEMBER='true'
CONFIGURE_CLIENT='true'

function show_help(){
cat > /dev/stdout << END
${0} --cert-dir - Name of directory containing certificates:- default ${CERT_DIR}
--help - show help
EXAMPLES
- "Generate configs"
  ./generate_configs.sh --cert-dir ${CERT_DIR}
END
}


while [[ $# -gt 0 ]]; do
    arg="$1"
    case $arg in
        --cert-dir)
            CERT_DIR="$2"
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

# sanity checks
if [[ -z "${CERT_DIR}" ]] ; then
    echo "Missing required argument CERT_DIR"
    exit 1
fi

# Create BASE_DIR
BASE_DIR="$(pwd)/${CERT_DIR}"
mkdir -p "${BASE_DIR}"

BASE_CA_DIR="${BASE_DIR}"/bdb-cluster-ca
BASE_MEMBER_CERT_DIR="${BASE_DIR}"/member-cert
BASE_CLIENT_CERT_DIR="${BASE_DIR}"/client-cert
BASE_EASY_RSA_PATH='easy-rsa-3.0.1/easyrsa3'
BASE_K8S_DIR="${BASE_DIR}"/k8s
BASE_USERS_DIR="$BASE_DIR"/users

# Configure Root CA
mkdir $BASE_CA_DIR
configure_common $BASE_CA_DIR
configure_root_ca $BASE_CA_DIR/$BASE_EASY_RSA_PATH


# Configure Member Request/Key generation
mkdir $BASE_MEMBER_CERT_DIR
configure_common $BASE_MEMBER_CERT_DIR
configure_member_cert_gen $BASE_MEMBER_CERT_DIR/$BASE_EASY_RSA_PATH

# Configure Client Request/Key generation
mkdir $BASE_CLIENT_CERT_DIR
configure_common $BASE_CLIENT_CERT_DIR
configure_client_cert_gen $BASE_CLIENT_CERT_DIR/$BASE_EASY_RSA_PATH

import_requests $BASE_CA_DIR/$BASE_EASY_RSA_PATH
sign_requests $BASE_CA_DIR/$BASE_EASY_RSA_PATH
make_pem_files $BASE_CA_DIR/$BASE_EASY_RSA_PATH $BASE_K8S_DIR
convert_b64 $BASE_K8S_DIR $BASE_CA_DIR/$BASE_EASY_RSA_PATH $BASE_CLIENT_CERT_DIR/$BASE_EASY_RSA_PATH

get_users $BASE_USERS_DIR $BASE_CA_DIR/$BASE_EASY_RSA_PATH
generate_secretes_no_threescale $BASE_K8S_DIR $SECRET_TOKEN $HTTPS_CERT_KEY_FILE_NAME $HTTPS_CERT_CHAIN_FILE_NAME $MDB_ADMIN_PASSWORD

generate_config_map $BASE_USERS_DIR $MDB_ADMIN_USER $NODE_FQDN $TM_SEEDS $TM_VALIDATORS $TM_VALIDATOR_POWERS $TM_GENESIS_TIME $TM_CHAIN_ID $TM_INSTANCE_NAME
