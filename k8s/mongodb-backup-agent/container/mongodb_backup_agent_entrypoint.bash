#!/bin/bash

set -euo pipefail

MONGODB_BACKUP_CONF_FILE=/etc/mongodb-mms/backup-agent.config

mms_api_keyfile_path=`printenv MMS_API_KEYFILE_PATH`
mms_groupid_keyfile_path=`printenv MMS_GROUPID_KEYFILE_PATH`
ca_crt_path=`printenv CA_CRT_PATH`
backup_pem_path=`printenv BACKUP_PEM_PATH`

if [[ -z "${mms_api_keyfile_path:?MMS_API_KEYFILE_PATH not specified. Exiting!}" || \
    -z "${ca_crt_path:?CA_CRT_PATH not specified. Exiting!}" || \
    -z "${backup_pem_path:?BACKUP_PEM_PATH not specified. Exiting!}" || \
    -z "${mms_groupid_keyfile_path:?MMS_GROUPID_KEYFILE_PATH not specified. Exiting!}" ]]; then
  exit 1
else
  echo MMS_API_KEYFILE_PATH="$mms_api_keyfile_path"
  echo MMS_GROUPID_KEYFILE_PATH="$mms_groupid_keyfile_path"
  echo CA_CRT_PATH="$ca_crt_path"
  echo BACKUP_PEM_PATH="$backup_pem_path"
fi

sed -i '/mmsApiKey/d'  ${MONGODB_BACKUP_CONF_FILE}
sed -i '/mmsGroupId/d'  ${MONGODB_BACKUP_CONF_FILE}
sed -i '/mothership/d'  ${MONGODB_BACKUP_CONF_FILE}

# Get the api key from file
mms_api_key=`cat ${mms_api_keyfile_path}`
mms_groupid_key=`cat ${mms_groupid_keyfile_path}`

echo "mmsApiKey="${mms_api_key} >> ${MONGODB_BACKUP_CONF_FILE}
echo "mmsGroupId="${mms_groupid_key} >> ${MONGODB_BACKUP_CONF_FILE}
echo "mothership=api-backup.eu-west-1.mongodb.com" >> ${MONGODB_BACKUP_CONF_FILE}

# Append SSL settings to the config file
echo "useSslForAllConnections=true" >> ${MONGODB_BACKUP_CONF_FILE}
echo "sslRequireValidServerCertificates=true" >> ${MONGODB_BACKUP_CONF_FILE}
echo "sslTrustedServerCertificates="${ca_crt_path} >> ${MONGODB_BACKUP_CONF_FILE}
echo "sslClientCertificate="${backup_pem_path} >> ${MONGODB_BACKUP_CONF_FILE}
echo "#sslClientCertificatePassword=<password>" >> ${MONGODB_BACKUP_CONF_FILE}

echo "INFO: starting mdb backup..."
exec mongodb-mms-backup-agent -c $MONGODB_BACKUP_CONF_FILE
