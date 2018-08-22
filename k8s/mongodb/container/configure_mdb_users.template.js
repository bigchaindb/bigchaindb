// Copyright BigchainDB GmbH and BigchainDB contributors
// SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
// Code is Apache-2.0 and docs are CC-BY-4.0

var configure_adminUser = CONFIGURE_ADMIN_USER;
var configure_bdbUser = CONFIGURE_BDB_USER;
var configure_mdbMonUser = CONFIGURE_MDB_MON_USER;
db = db.getSiblingDB("admin");

if (configure_adminUser) {
    db.createUser({
        user: "MONGODB_ADMIN_USERNAME",
        pwd: "MONGODB_ADMIN_PASSWORD",
        roles: [{
                role: "userAdminAnyDatabase",
                db: "admin"
            },
            {
                role: "clusterManager",
                db: "admin"
            }
        ]
    });
}
if (configure_adminUser && configure_bdbUser) {
    db.auth("MONGODB_ADMIN_USERNAME", "MONGODB_ADMIN_PASSWORD");
    db.getSiblingDB("$external").runCommand({
        createUser: 'BDB_USERNAME',
        writeConcern: {
            w: 'majority',
            wtimeout: 5000
        },
        roles: [{
                role: 'clusterAdmin',
                db: 'admin'
            },
            {
                role: 'readWriteAnyDatabase',
                db: 'admin'
            }
        ]
    });
}
if (configure_adminUser && configure_mdbMonUser) {
    db.auth("MONGODB_ADMIN_USERNAME", "MONGODB_ADMIN_PASSWORD");
    db.getSiblingDB("$external").runCommand({
        createUser: 'MDB_MON_USERNAME',
        writeConcern: {
            w: 'majority',
            wtimeout: 5000
        },
        roles: [{
            role: 'clusterMonitor',
            db: 'admin'
        }]
    });
}