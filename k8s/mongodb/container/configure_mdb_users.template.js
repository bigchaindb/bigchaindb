db = db.getSiblingDB("admin");
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
db = db.getSiblingDB("admin");
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