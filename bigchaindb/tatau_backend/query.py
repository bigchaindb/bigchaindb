"""Tatau Query implementation for MongoDB"""


def aggregate(conn, pipeline, table='transactions'):
    cursor = conn.run(
        conn.collection(table).aggregate(pipeline))

    return (obj for obj in cursor)