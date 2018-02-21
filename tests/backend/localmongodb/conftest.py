from pymongo import MongoClient
from pytest import fixture


@fixture
def mongo_client(db_context):
    return MongoClient(host=db_context.host, port=db_context.port)


@fixture
def utxo_collection(db_context, mongo_client):
    return mongo_client[db_context.name].utxos
