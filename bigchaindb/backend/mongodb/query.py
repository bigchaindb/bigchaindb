from bigchaindb.backend import query
from bigchaindb.backend.mongodb.connection import MongoDBConnection


@query.write_transaction.register(MongoDBConnection)
def write_transaction(conn, signed_transaction):
    return conn.db['backlog'].insert_one(signed_transaction)


@query.write_vote.register(MongoDBConnection)
def write_vote(conn, vote):
    return conn.db['votes'].insert_one(vote)


@query.write_block.register(MongoDBConnection)
def write_block(conn, block):
    return conn.db['bigchain'].insert_one(block.to_dict())


@query.genesis_block_exists.register(MongoDBConnection)
def genesis_block_exists(conn):
    return conn.db['bigchain'].count() > 0


@query.search_block_election_on_index.register(MongoDBConnection)
def search_block_election_on_index(conn, value, index):
    return conn.db['bigchain']\
        .find({index: value}, projection={'votes', 'id', 'block.voters'})


@query.get_votes_on_block.register(MongoDBConnection)
def get_votes_on_block(conn, block_id):
    return conn.db['votes'].find({'vote.voting_for_block': block_id})


@query.transaction_exists.register(MongoDBConnection)
def transaction_exists(conn, transaction_id):
    if conn.db['bigchain']\
       .find_one({'block.transactions.id': transaction_id}):
        return True
    else:
        return False
