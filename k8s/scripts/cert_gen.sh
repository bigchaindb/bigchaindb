#!/usr/bin/env bash
set -e
set -o xtrace


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


function show_help(){
cat > /dev/stdout << END
${0} --index INDEX --mdb-name MONGODB_MEMBER_COMMON_NAME
--bdb-name BIGCHAINDB_INSTANCE_COMMON_NAME
--mdb-mon-name MONGODB_MONITORING_INSTNACE_COMMON_NAME [--help]
OPTIONAL ARGS:
--mdb-cn - Common name of MongoDB instance:- default ${MDB_CN}
--bdb-cn - Common name of BigchainDB instance:- default ${BDB_CN}
--mdb-mon-cn - Common name of MongoDB monitoring agent:- default ${MDB_MON_CN}
--dir - Absolute path of base directory:- default ${pwd}
--help - show help
EXAMPLES
- "Generate Certificates for first node(index=1) in the cluster i.e. MongoDB instance: mdb-instance,"
  "BigchainDB instance: bdb-instance, MongoDB monitoring agent: mdb-mon-instance"
  ./cert_gen.sh --index 1 --mdb-cn mdb-instance --bdb-cn bdb-instance \
  --mdb-mon-cn mdb-mon-instance
END
}

function configure_root_ca(){
    # $1:- Base directory for Root CA
    echo "Generate Root CA"
    echo 'set_var EASYRSA_DN "org"' >> $1/vars
    echo 'set_var EASYRSA_KEY_SIZE 4096' >> $1/vars

    #TODO: Parametrize the below configurations
    echo 'set_var EASYRSA_REQ_COUNTRY "DE"' >> $1/vars
    echo 'set_var EASYRSA_REQ_PROVINCE "Berlin"' >> $1/vars
    echo 'set_var EASYRSA_REQ_CITY "Berlin"' >> $1/vars
    echo 'set_var EASYRSA_REQ_ORG "BigchainDB GmbH"' >> $1/vars
    echo 'set_var EASYRSA_REQ_OU "ROOT-CA"' >> $1/vars
    echo 'set_var EASYRSA_REQ_EMAIL "dev@bigchaindb.com"' >> $1//vars

    sed -i.bk '/^extendedKeyUsage/ s/$/,clientAuth/' $1/x509-types/server
    echo "set_var EASYRSA_SSL_CONF \"$1/openssl-1.0.cnf\"" >> $1/vars
    echo "set_var EASYRSA_PKI \"$1/pki\"" >> $1/vars
    echo "set_var EASYRSA_EXT_DIR \"$1/x509-types\"" >> $1/vars
    $1/easyrsa init-pki
    $1/easyrsa build-ca
    $1/easyrsa gen-crl
}

function configure_member_cert_gen(){
    # $1:- Base directory for MongoDB Member Requests/Keys
    echo "Generate MongoDB Member Requests/Certificate(s)"
    echo 'set_var EASYRSA_DN "org"' >> $1/vars
    echo 'set_var EASYRSA_KEY_SIZE 4096' >> $1/vars

    #TODO: Parametrize the below configurations
    echo 'set_var EASYRSA_REQ_COUNTRY "DE"' >> $1/vars
    echo 'set_var EASYRSA_REQ_PROVINCE "Berlin"' >> $1/vars
    echo 'set_var EASYRSA_REQ_CITY "Berlin"' >> $1/vars
    echo 'set_var EASYRSA_REQ_ORG "BigchainDB GmbH"' >> $1/vars
    echo 'set_var EASYRSA_REQ_OU "MONGO-MEMBER"' >> $1/vars
    echo 'set_var EASYRSA_REQ_EMAIL "dev@bigchaindb.com"' >> $1/vars
    echo "set_var EASYRSA_SSL_CONF \"$1/openssl-1.0.cnf\"" >> $1/vars
    echo "set_var EASYRSA_PKI \"$1/pki\"" >> member-cert/easy-rsa-3.0.1/easyrsa3/vars
    $1/easyrsa init-pki
    $1/easyrsa --req-cn="$MDB_CN"-"$INDEX" --subject-alt-name=DNS:localhost,DNS:"$MDB_CN"-"$INDEX" gen-req "$MDB_CN"-"$INDEX" nopass
}

function configure_client_cert_gen(){
    # $1:- Base directory for MongoDB Client Requests/Keys
    echo "Generate MongoDB Client  Requests/Certificate(s)"
    echo 'set_var EASYRSA_DN "org"' >> $1/vars
    echo 'set_var EASYRSA_KEY_SIZE 4096' >> $1/vars

    #TODO: Parametrize the below configurations
    echo 'set_var EASYRSA_REQ_COUNTRY "DE"' >> $1/vars
    echo 'set_var EASYRSA_REQ_PROVINCE "Berlin"' >> $1/vars
    echo 'set_var EASYRSA_REQ_CITY "Berlin"' >> $1/vars
    echo 'set_var EASYRSA_REQ_ORG "BigchainDB GmbH"' >> $1/vars
    echo 'set_var EASYRSA_REQ_OU "MONGO-CLIENT"' >> $1/vars
    echo 'set_var EASYRSA_REQ_EMAIL "dev@bigchaindb.com"' >> $1/vars
    echo "set_var EASYRSA_SSL_CONF \"$1/openssl-1.0.cnf\"" >> $1/vars
    echo "set_var EASYRSA_PKI \"$1/pki\"" >> $1/vars
    $1/easyrsa init-pki
    $1/easyrsa gen-req "$BDB_CN"-"$INDEX" nopass
    $1/easyrsa gen-req "$MDB_MON_CN"-"$INDEX" nopass
}

function import_requests(){
    # $1:- Base directory for Root CA
    $1/easyrsa import-req $BASE_MEMBER_CERT_DIR/$BASE_EASY_RSA_PATH/pki/reqs/"$MDB_CN"-"$INDEX".req "$MDB_CN"-"$INDEX"
    $1/easyrsa import-req $BASE_CLIENT_CERT_DIR/$BASE_EASY_RSA_PATH/pki/reqs/"$BDB_CN"-"$INDEX".req "$BDB_CN"-"$INDEX"
    $1/easyrsa import-req $BASE_CLIENT_CERT_DIR/$BASE_EASY_RSA_PATH/pki/reqs/"$MDB_MON_CN"-"$INDEX".req "$MDB_MON_CN"-"$INDEX"
}

function sign_requests(){
    # $1:- Base directory for Root CA
    $1/easyrsa --subject-alt-name=DNS:localhost,DNS:"$MDB_CN"-"$INDEX" sign-req server "$MDB_CN"-"$INDEX"
    $1/easyrsa sign-req client "$BDB_CN"-"$INDEX"
    $1/easyrsa sign-req client "$MDB_MON_CN"-"$INDEX"
}

function make_pem_files(){
    # $1:- Base directory for Root CA
    # $2:- Base directory for kubernetes related config for secret.yaml
    mkdir $2
    cat $1/pki/issued/"$MDB_CN"-"$INDEX".crt $BASE_MEMBER_CERT_DIR/$BASE_EASY_RSA_PATH/pki/private/"$MDB_CN"-"$INDEX".key > $2/"$MDB_CN"-"$INDEX".pem
    cat $1/pki/issued/"$BDB_CN"-"$INDEX".crt $BASE_CLIENT_CERT_DIR/$BASE_EASY_RSA_PATH/pki/private/"$BDB_CN"-"$INDEX".key > $2/"$BDB_CN"-"$INDEX".pem
    cat $1/pki/issued/"$MDB_MON_CN"-"$INDEX".crt $BASE_CLIENT_CERT_DIR/$BASE_EASY_RSA_PATH/pki/private/"$MDB_MON_CN"-"$INDEX".key > $2/"$MDB_MON_CN"-"$INDEX".pem
}

function convert_b64(){
    # $1:- Base directory for kubernetes related config for secret.yaml
    # $2:- Base directory for Root CA
    # $3:- Base directory for client requests/keys
    cat $1/"$MDB_CN"-"$INDEX".pem | base64 -w 0 > $1/"$MDB_CN"-"$INDEX".pem.b64
    cat $1/"$BDB_CN"-"$INDEX".pem | base64 -w 0 > $1/"$BDB_CN"-"$INDEX".pem.b64
    cat $1/"$MDB_MON_CN"-"$INDEX".pem | base64 -w 0 > $1/"$MDB_MON_CN"-"$INDEX".pem.b64

    cat $3/pki/private/"$BDB_CN"-"$INDEX".key | base64 -w 0 > $1/"$BDB_CN"-"$INDEX".key.b64
    cat $2/pki/ca.crt | base64 -w 0 > $1/ca.crt.b64
    cat $2/pki/crl.pem | base64 -w 0 > $1/crl.pem.b64
}

function get_users(){
    openssl x509 -in $BASE_CA_DIR/$BASE_EASY_RSA_PATH/pki/issued/"$MDB_CN"-"$INDEX".crt -inform PEM -subject \
      -nameopt RFC2253 | head -n 1 | sed -r 's/^subject= //' > $1/"$MDB_CN"-"$INDEX".user
    openssl x509 -in $BASE_CA_DIR/$BASE_EASY_RSA_PATH/pki/issued/"$BDB_CN"-"$INDEX".crt -inform PEM -subject \
      -nameopt RFC2253 | head -n 1 | sed -r 's/^subject= //' > $1/"$BDB_CN"-"$INDEX".user
    openssl x509 -in $BASE_CA_DIR/$BASE_EASY_RSA_PATH/pki/issued/"$MDB_MON_CN"-"$INDEX".crt -inform PEM -subject \
      -nameopt RFC2253 | head -n 1 | sed -r 's/^subject= //' > $1/"$MDB_MON_CN"-"$INDEX".user

}

function configure_common(){
    sudo apt-get update -y
    sudo apt-get install openssl -y
    wget https://github.com/OpenVPN/easy-rsa/archive/3.0.1.tar.gz -P $1
    tar xzvf $1/3.0.1.tar.gz -C $1/
    rm $1/3.0.1.tar.gz
    cp $1/$BASE_EASY_RSA_PATH/vars.example $1/$BASE_EASY_RSA_PATH/vars
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
BASE_USERS_DIR="{$BASE_DIR}"/users

# sanity checks
if [[ -z "${INDEX}" ]] ; then
    echo "Missing required arguments"
    exit 1
fi

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