import pytest


@pytest.fixture
def config(request, monkeypatch):
    config = {
        'database': {
            'backend': request.config.getoption('--database-backend'),
            'host': 'host',
            'port': 28015,
            'name': 'bigchain',
            'replicaset': 'bigchain-rs',
            'connection_timeout': 5000,
            'max_tries': 3
        },
        'keypair': {
            'public': 'pubkey',
            'private': 'privkey',
        },
        'keyring': [],
        'CONFIGURED': True,
        'backlog_reassign_delay': 30
    }

    monkeypatch.setattr('bigchaindb.config', config)

    return config


def test_bigchain_class_default_initialization(config):
    from bigchaindb.core import Bigchain
    from bigchaindb.consensus import BaseConsensusRules
    from bigchaindb.backend.connection import Connection
    bigchain = Bigchain()
    assert isinstance(bigchain.connection, Connection)
    assert bigchain.connection.host == config['database']['host']
    assert bigchain.connection.port == config['database']['port']
    assert bigchain.connection.dbname == config['database']['name']
    assert bigchain.me == config['keypair']['public']
    assert bigchain.me_private == config['keypair']['private']
    assert bigchain.nodes_except_me == config['keyring']
    assert bigchain.consensus == BaseConsensusRules


def test_bigchain_class_initialization_with_parameters(config):
    from bigchaindb.core import Bigchain
    from bigchaindb.backend import connect
    from bigchaindb.consensus import BaseConsensusRules
    init_kwargs = {
        'public_key': 'white',
        'private_key': 'black',
        'keyring': ['key_one', 'key_two'],
    }
    init_db_kwargs = {
        'backend': 'rethinkdb',
        'host': 'this_is_the_db_host',
        'port': 12345,
        'name': 'this_is_the_db_name',
    }
    connection = connect(**init_db_kwargs)
    bigchain = Bigchain(connection=connection, **init_kwargs)
    assert bigchain.connection == connection
    assert bigchain.connection.host == init_db_kwargs['host']
    assert bigchain.connection.port == init_db_kwargs['port']
    assert bigchain.connection.dbname == init_db_kwargs['name']
    assert bigchain.me == init_kwargs['public_key']
    assert bigchain.me_private == init_kwargs['private_key']
    assert bigchain.nodes_except_me == init_kwargs['keyring']
    assert bigchain.consensus == BaseConsensusRules


def test_get_blocks_status_containing_tx(monkeypatch):
    from bigchaindb.backend import query as backend_query
    from bigchaindb.core import Bigchain
    blocks = [
        {'id': 1}, {'id': 2}
    ]
    monkeypatch.setattr(backend_query, 'get_blocks_status_from_transaction', lambda x: blocks)
    monkeypatch.setattr(Bigchain, 'block_election_status', lambda x, y, z: Bigchain.BLOCK_VALID)
    bigchain = Bigchain(public_key='pubkey', private_key='privkey')
    with pytest.raises(Exception):
        bigchain.get_blocks_status_containing_tx('txid')


###############################################################################
#                                                                             #
#   get_spent                                                                 #
#                                                                             #
###############################################################################
@pytest.mark.genesis
def test_get_spent_with_double_inclusion_detected(b, monkeypatch):
    from bigchaindb.exceptions import CriticalDoubleInclusion
    from bigchaindb.models import Transaction

    tx = Transaction.create([b.me], [([b.me], 1)])
    tx = tx.sign([b.me_private])

    monkeypatch.setattr('time.time', lambda: 1000000000)
    block1 = b.create_block([tx])
    b.write_block(block1)

    monkeypatch.setattr('time.time', lambda: 1000000020)
    transfer_tx = Transaction.transfer(tx.to_inputs(), [([b.me], 1)],
                                       asset_id=tx.id)
    transfer_tx = transfer_tx.sign([b.me_private])
    block2 = b.create_block([transfer_tx])
    b.write_block(block2)

    monkeypatch.setattr('time.time', lambda: 1000000030)
    transfer_tx2 = Transaction.transfer(tx.to_inputs(), [([b.me], 1)],
                                        asset_id=tx.id)
    transfer_tx2 = transfer_tx2.sign([b.me_private])
    block3 = b.create_block([transfer_tx2])
    b.write_block(block3)

    # Vote both block2 and block3 valid
    vote = b.vote(block2.id, b.get_last_voted_block().id, True)
    b.write_vote(vote)
    vote = b.vote(block3.id, b.get_last_voted_block().id, True)
    b.write_vote(vote)

    with pytest.raises(CriticalDoubleInclusion):
        b.get_spent(tx.id, 0)


@pytest.mark.genesis
def test_get_spent_with_double_spend_detected(b, monkeypatch):
    from bigchaindb.exceptions import CriticalDoubleSpend
    from bigchaindb.models import Transaction

    tx = Transaction.create([b.me], [([b.me], 1)])
    tx = tx.sign([b.me_private])

    monkeypatch.setattr('time.time', lambda: 1000000000)
    block1 = b.create_block([tx])
    b.write_block(block1)

    monkeypatch.setattr('time.time', lambda: 1000000020)
    transfer_tx = Transaction.transfer(tx.to_inputs(), [([b.me], 1)],
                                       asset_id=tx.id)
    transfer_tx = transfer_tx.sign([b.me_private])
    block2 = b.create_block([transfer_tx])
    b.write_block(block2)

    monkeypatch.setattr('time.time', lambda: 1000000030)
    transfer_tx2 = Transaction.transfer(tx.to_inputs(), [([b.me], 2)],
                                        asset_id=tx.id)
    transfer_tx2 = transfer_tx2.sign([b.me_private])
    block3 = b.create_block([transfer_tx2])
    b.write_block(block3)

    # Vote both block2 and block3 valid
    vote = b.vote(block2.id, b.get_last_voted_block().id, True)
    b.write_vote(vote)
    vote = b.vote(block3.id, b.get_last_voted_block().id, True)
    b.write_vote(vote)

    with pytest.raises(CriticalDoubleSpend):
        b.get_spent(tx.id, 0)


@pytest.mark.bdb
def test_get_spent_single_tx_single_output(b, user_sk, user_pk):
    from bigchaindb.common import crypto
    from bigchaindb.models import Transaction

    user2_sk, user2_pk = crypto.generate_key_pair()

    tx = Transaction.create([b.me], [([user_pk], 1)])
    tx = tx.sign([b.me_private])
    block = b.create_block([tx])
    b.write_block(block)

    owned_inputs_user1 = b.get_owned_ids(user_pk).pop()

    # check spents
    input_txid = owned_inputs_user1.txid
    input_idx = owned_inputs_user1.output
    spent_inputs_user1 = b.get_spent(input_txid, input_idx)
    assert spent_inputs_user1 is None

    # create a transaction and block
    tx = Transaction.transfer(tx.to_inputs(), [([user2_pk], 1)],
                              asset_id=tx.id)
    tx = tx.sign([user_sk])
    block = b.create_block([tx])
    b.write_block(block)

    spent_inputs_user1 = b.get_spent(input_txid, input_idx)
    assert spent_inputs_user1 == tx


@pytest.mark.bdb
def test_get_spent_single_tx_single_output_invalid_block(b,
                                                         user_sk,
                                                         user_pk,
                                                         genesis_block):
    from bigchaindb.common import crypto
    from bigchaindb.models import Transaction

    # create a new users
    user2_sk, user2_pk = crypto.generate_key_pair()

    tx = Transaction.create([b.me], [([user_pk], 1)])
    tx = tx.sign([b.me_private])
    block = b.create_block([tx])
    b.write_block(block)

    # vote the block VALID
    vote = b.vote(block.id, genesis_block.id, True)
    b.write_vote(vote)

    owned_inputs_user1 = b.get_owned_ids(user_pk).pop()

    # check spents
    input_txid = owned_inputs_user1.txid
    input_idx = owned_inputs_user1.output
    spent_inputs_user1 = b.get_spent(input_txid, input_idx)
    assert spent_inputs_user1 is None

    # create a transaction and block
    tx = Transaction.transfer(tx.to_inputs(), [([user2_pk], 1)],
                              asset_id=tx.id)
    tx = tx.sign([user_sk])
    block = b.create_block([tx])
    b.write_block(block)

    # vote the block invalid
    vote = b.vote(block.id, b.get_last_voted_block().id, False)
    b.write_vote(vote)
    # NOTE: I have no idea why this line is here
    b.get_transaction(tx.id)
    spent_inputs_user1 = b.get_spent(input_txid, input_idx)

    # Now there should be no spents (the block is invalid)
    assert spent_inputs_user1 is None


@pytest.mark.bdb
def test_get_spent_single_tx_multiple_outputs(b, user_sk, user_pk):
    from bigchaindb.common import crypto
    from bigchaindb.models import Transaction

    # create a new users
    user2_sk, user2_pk = crypto.generate_key_pair()

    # create a divisible asset with 3 outputs
    tx_create = Transaction.create([b.me],
                                   [([user_pk], 1),
                                    ([user_pk], 1),
                                    ([user_pk], 1)])
    tx_create_signed = tx_create.sign([b.me_private])
    block = b.create_block([tx_create_signed])
    b.write_block(block)

    owned_inputs_user1 = b.get_owned_ids(user_pk)

    # check spents
    for input_tx in owned_inputs_user1:
        assert b.get_spent(input_tx.txid, input_tx.output) is None

    # transfer the first 2 inputs
    tx_transfer = Transaction.transfer(tx_create.to_inputs()[:2],
                                       [([user2_pk], 1), ([user2_pk], 1)],
                                       asset_id=tx_create.id)
    tx_transfer_signed = tx_transfer.sign([user_sk])
    block = b.create_block([tx_transfer_signed])
    b.write_block(block)

    # check that used inputs are marked as spent
    for ffill in tx_create.to_inputs()[:2]:
        spent_tx = b.get_spent(ffill.fulfills.txid, ffill.fulfills.output)
        assert spent_tx == tx_transfer_signed

    # check if remaining transaction that was unspent is also perceived
    # spendable by BigchainDB
    assert b.get_spent(tx_create.to_inputs()[2].fulfills.txid, 2) is None


@pytest.mark.bdb
def test_get_spent_multiple_owners(b, user_sk, user_pk):
    from bigchaindb.common import crypto
    from bigchaindb.models import Transaction

    user2_sk, user2_pk = crypto.generate_key_pair()
    user3_sk, user3_pk = crypto.generate_key_pair()

    transactions = []
    for i in range(3):
        payload = {'somedata': i}
        tx = Transaction.create([b.me], [([user_pk, user2_pk], 1)],
                                payload)
        tx = tx.sign([b.me_private])
        transactions.append(tx)
    block = b.create_block(transactions)
    b.write_block(block)

    owned_inputs_user1 = b.get_owned_ids(user_pk)

    # check spents
    for input_tx in owned_inputs_user1:
        assert b.get_spent(input_tx.txid, input_tx.output) is None

    # create a transaction
    tx = Transaction.transfer(transactions[0].to_inputs(),
                              [([user3_pk], 1)],
                              asset_id=transactions[0].id)
    tx = tx.sign([user_sk, user2_sk])
    block = b.create_block([tx])
    b.write_block(block)

    # check that used inputs are marked as spent
    assert b.get_spent(transactions[0].id, 0) == tx

    # check that the other remain marked as unspent
    for unspent in transactions[1:]:
        assert b.get_spent(unspent.id, 0) is None
