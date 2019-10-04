# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

import json
import pytest
import random

from abci import (
    PubKey,
    ResponseInitChain,
    RequestInitChain,
    RequestInfo,
    RequestBeginBlock,
    RequestEndBlock,
    ValidatorUpdate,
)

from bigchaindb import App
from bigchaindb.backend.localmongodb import query
from bigchaindb.common.crypto import generate_key_pair
from bigchaindb.core import (CodeTypeOk,
                             CodeTypeError,
                             rollback
                             )
from bigchaindb.elections.election import Election
from bigchaindb.lib import Block
from bigchaindb.migrations.chain_migration_election import ChainMigrationElection
from bigchaindb.upsert_validator.validator_election import ValidatorElection
from bigchaindb.upsert_validator.validator_utils import new_validator_set
from bigchaindb.tendermint_utils import public_key_to_base64
from bigchaindb.version import __tm_supported_versions__

from tests.utils import generate_election, generate_validators


pytestmark = pytest.mark.bdb


def encode_tx_to_bytes(transaction):
    return json.dumps(transaction.to_dict()).encode('utf8')


def generate_address():
    return ''.join(random.choices('1,2,3,4,5,6,7,8,9,A,B,C,D,E,F'.split(','),
                                  k=40)).encode()


def generate_validator():
    pk, _ = generate_key_pair()
    pub_key = PubKey(type='ed25519', data=pk.encode())
    val = ValidatorUpdate(power=10, pub_key=pub_key)
    return val


def generate_init_chain_request(chain_id, vals=None):
    vals = vals if vals is not None else [generate_validator()]
    return RequestInitChain(validators=vals, chain_id=chain_id)


def test_init_chain_successfully_registers_chain(b):
    request = generate_init_chain_request('chain-XYZ')
    res = App(b).init_chain(request)
    assert res == ResponseInitChain()
    chain = query.get_latest_abci_chain(b.connection)
    assert chain == {'height': 0, 'chain_id': 'chain-XYZ', 'is_synced': True}
    assert query.get_latest_block(b.connection) == {
        'height': 0,
        'app_hash': '',
        'transactions': [],
    }


def test_init_chain_ignores_invalid_init_chain_requests(b):
    validators = [generate_validator()]
    request = generate_init_chain_request('chain-XYZ', validators)
    res = App(b).init_chain(request)
    assert res == ResponseInitChain()

    validator_set = query.get_validator_set(b.connection)

    invalid_requests = [
        request,  # the same request again
        # different validator set
        generate_init_chain_request('chain-XYZ'),
        # different chain ID
        generate_init_chain_request('chain-ABC', validators),
    ]
    for r in invalid_requests:
        with pytest.raises(SystemExit):
            App(b).init_chain(r)
        # assert nothing changed - neither validator set, nor chain ID
        new_validator_set = query.get_validator_set(b.connection)
        assert new_validator_set == validator_set
        new_chain_id = query.get_latest_abci_chain(b.connection)['chain_id']
        assert new_chain_id == 'chain-XYZ'
        assert query.get_latest_block(b.connection) == {
            'height': 0,
            'app_hash': '',
            'transactions': [],
        }


def test_init_chain_recognizes_new_chain_after_migration(b):
    validators = [generate_validator()]
    request = generate_init_chain_request('chain-XYZ', validators)
    res = App(b).init_chain(request)
    assert res == ResponseInitChain()

    validator_set = query.get_validator_set(b.connection)['validators']

    # simulate a migration
    query.store_block(b.connection, Block(app_hash='', height=1,
                                          transactions=[])._asdict())
    b.migrate_abci_chain()

    # the same or other mismatching requests are ignored
    invalid_requests = [
        request,
        generate_init_chain_request('unknown', validators),
        generate_init_chain_request('chain-XYZ'),
        generate_init_chain_request('chain-XYZ-migrated-at-height-1'),
    ]
    for r in invalid_requests:
        with pytest.raises(SystemExit):
            App(b).init_chain(r)
        assert query.get_latest_abci_chain(b.connection) == {
            'chain_id': 'chain-XYZ-migrated-at-height-1',
            'is_synced': False,
            'height': 2,
        }
        new_validator_set = query.get_validator_set(b.connection)['validators']
        assert new_validator_set == validator_set

    # a request with the matching chain ID and matching validator set
    # completes the migration
    request = generate_init_chain_request('chain-XYZ-migrated-at-height-1',
                                          validators)
    res = App(b).init_chain(request)
    assert res == ResponseInitChain()
    assert query.get_latest_abci_chain(b.connection) == {
        'chain_id': 'chain-XYZ-migrated-at-height-1',
        'is_synced': True,
        'height': 2,
    }
    assert query.get_latest_block(b.connection) == {
        'height': 2,
        'app_hash': '',
        'transactions': [],
    }

    # requests with old chain ID and other requests are ignored
    invalid_requests = [
        request,
        generate_init_chain_request('chain-XYZ', validators),
        generate_init_chain_request('chain-XYZ-migrated-at-height-1'),
    ]
    for r in invalid_requests:
        with pytest.raises(SystemExit):
            App(b).init_chain(r)
        assert query.get_latest_abci_chain(b.connection) == {
            'chain_id': 'chain-XYZ-migrated-at-height-1',
            'is_synced': True,
            'height': 2,
        }
        new_validator_set = query.get_validator_set(b.connection)['validators']
        assert new_validator_set == validator_set
        assert query.get_latest_block(b.connection) == {
            'height': 2,
            'app_hash': '',
            'transactions': [],
        }


def test_info(b):
    r = RequestInfo(version=__tm_supported_versions__[0])
    app = App(b)

    res = app.info(r)
    assert res.last_block_height == 0
    assert res.last_block_app_hash == b''

    b.store_block(Block(app_hash='1', height=1, transactions=[])._asdict())
    res = app.info(r)
    assert res.last_block_height == 1
    assert res.last_block_app_hash == b'1'

    # simulate a migration and assert the height is shifted
    b.store_abci_chain(2, 'chain-XYZ')
    app = App(b)
    b.store_block(Block(app_hash='2', height=2, transactions=[])._asdict())
    res = app.info(r)
    assert res.last_block_height == 0
    assert res.last_block_app_hash == b'2'

    b.store_block(Block(app_hash='3', height=3, transactions=[])._asdict())
    res = app.info(r)
    assert res.last_block_height == 1
    assert res.last_block_app_hash == b'3'

    # it's always the latest migration that is taken into account
    b.store_abci_chain(4, 'chain-XYZ-new')
    app = App(b)
    b.store_block(Block(app_hash='4', height=4, transactions=[])._asdict())
    res = app.info(r)
    assert res.last_block_height == 0
    assert res.last_block_app_hash == b'4'


def test_check_tx__signed_create_is_ok(b):
    from bigchaindb import App
    from bigchaindb.models import Transaction
    from bigchaindb.common.crypto import generate_key_pair

    alice = generate_key_pair()
    bob = generate_key_pair()

    tx = Transaction.create([alice.public_key],
                            [([bob.public_key], 1)])\
                    .sign([alice.private_key])

    app = App(b)
    result = app.check_tx(encode_tx_to_bytes(tx))
    assert result.code == CodeTypeOk


def test_check_tx__unsigned_create_is_error(b):
    from bigchaindb import App
    from bigchaindb.models import Transaction
    from bigchaindb.common.crypto import generate_key_pair

    alice = generate_key_pair()
    bob = generate_key_pair()

    tx = Transaction.create([alice.public_key],
                            [([bob.public_key], 1)])

    app = App(b)
    result = app.check_tx(encode_tx_to_bytes(tx))
    assert result.code == CodeTypeError


def test_deliver_tx__valid_create_updates_db_and_emits_event(b, init_chain_request):
    import multiprocessing as mp
    from bigchaindb import App
    from bigchaindb.models import Transaction
    from bigchaindb.common.crypto import generate_key_pair

    alice = generate_key_pair()
    bob = generate_key_pair()
    events = mp.Queue()

    tx = Transaction.create([alice.public_key],
                            [([bob.public_key], 1)])\
                    .sign([alice.private_key])

    app = App(b, events)

    app.init_chain(init_chain_request)

    begin_block = RequestBeginBlock()
    app.begin_block(begin_block)

    result = app.deliver_tx(encode_tx_to_bytes(tx))
    assert result.code == CodeTypeOk

    app.end_block(RequestEndBlock(height=99))
    app.commit()
    assert b.get_transaction(tx.id).id == tx.id
    block_event = events.get()
    assert block_event.data['transactions'] == [tx]

    # unspent_outputs = b.get_unspent_outputs()
    # unspent_output = next(unspent_outputs)
    # expected_unspent_output = next(tx.unspent_outputs)._asdict()
    # assert unspent_output == expected_unspent_output
    # with pytest.raises(StopIteration):
    #     next(unspent_outputs)


def test_deliver_tx__double_spend_fails(b, init_chain_request):
    from bigchaindb import App
    from bigchaindb.models import Transaction
    from bigchaindb.common.crypto import generate_key_pair

    alice = generate_key_pair()
    bob = generate_key_pair()

    tx = Transaction.create([alice.public_key],
                            [([bob.public_key], 1)])\
                    .sign([alice.private_key])

    app = App(b)
    app.init_chain(init_chain_request)

    begin_block = RequestBeginBlock()
    app.begin_block(begin_block)

    result = app.deliver_tx(encode_tx_to_bytes(tx))
    assert result.code == CodeTypeOk

    app.end_block(RequestEndBlock(height=99))
    app.commit()

    assert b.get_transaction(tx.id).id == tx.id
    result = app.deliver_tx(encode_tx_to_bytes(tx))
    assert result.code == CodeTypeError


def test_deliver_transfer_tx__double_spend_fails(b, init_chain_request):
    from bigchaindb import App
    from bigchaindb.models import Transaction
    from bigchaindb.common.crypto import generate_key_pair

    app = App(b)
    app.init_chain(init_chain_request)

    begin_block = RequestBeginBlock()
    app.begin_block(begin_block)

    alice = generate_key_pair()
    bob = generate_key_pair()
    carly = generate_key_pair()

    asset = {
        'msg': 'live long and prosper'
    }

    tx = Transaction.create([alice.public_key],
                            [([alice.public_key], 1)],
                            asset=asset)\
                    .sign([alice.private_key])

    result = app.deliver_tx(encode_tx_to_bytes(tx))
    assert result.code == CodeTypeOk

    tx_transfer = Transaction.transfer(tx.to_inputs(),
                                       [([bob.public_key], 1)],
                                       asset_id=tx.id)\
                             .sign([alice.private_key])

    result = app.deliver_tx(encode_tx_to_bytes(tx_transfer))
    assert result.code == CodeTypeOk

    double_spend = Transaction.transfer(tx.to_inputs(),
                                        [([carly.public_key], 1)],
                                        asset_id=tx.id)\
                              .sign([alice.private_key])

    result = app.deliver_tx(encode_tx_to_bytes(double_spend))
    assert result.code == CodeTypeError


def test_end_block_return_validator_updates(b, init_chain_request):
    app = App(b)
    app.init_chain(init_chain_request)

    begin_block = RequestBeginBlock()
    app.begin_block(begin_block)

    # generate a block containing a concluded validator election
    validators = generate_validators([1] * 4)
    b.store_validator_set(1, [v['storage'] for v in validators])

    new_validator = generate_validators([1])[0]

    public_key = validators[0]['public_key']
    private_key = validators[0]['private_key']
    voter_keys = [v['private_key'] for v in validators]

    election, votes = generate_election(b,
                                        ValidatorElection,
                                        public_key, private_key,
                                        new_validator['election'],
                                        voter_keys)
    b.store_block(Block(height=1, transactions=[election.id],
                        app_hash='')._asdict())
    b.store_bulk_transactions([election])
    Election.process_block(b, 1, [election])

    app.block_transactions = votes

    resp = app.end_block(RequestEndBlock(height=2))
    assert resp.validator_updates[0].power == new_validator['election']['power']
    expected = bytes.fromhex(new_validator['election']['public_key']['value'])
    assert expected == resp.validator_updates[0].pub_key.data


def test_store_pre_commit_state_in_end_block(b, alice, init_chain_request):
    from bigchaindb import App
    from bigchaindb.backend import query
    from bigchaindb.models import Transaction

    tx = Transaction.create([alice.public_key],
                            [([alice.public_key], 1)],
                            asset={'msg': 'live long and prosper'})\
                    .sign([alice.private_key])

    app = App(b)
    app.init_chain(init_chain_request)

    begin_block = RequestBeginBlock()
    app.begin_block(begin_block)
    app.deliver_tx(encode_tx_to_bytes(tx))
    app.end_block(RequestEndBlock(height=99))

    resp = query.get_pre_commit_state(b.connection)
    assert resp['height'] == 99
    assert resp['transactions'] == [tx.id]

    app.begin_block(begin_block)
    app.deliver_tx(encode_tx_to_bytes(tx))
    app.end_block(RequestEndBlock(height=100))
    resp = query.get_pre_commit_state(b.connection)
    assert resp['height'] == 100
    assert resp['transactions'] == [tx.id]

    # simulate a chain migration and assert the height is shifted
    b.store_abci_chain(100, 'new-chain')
    app = App(b)
    app.begin_block(begin_block)
    app.deliver_tx(encode_tx_to_bytes(tx))
    app.end_block(RequestEndBlock(height=1))
    resp = query.get_pre_commit_state(b.connection)
    assert resp['height'] == 101
    assert resp['transactions'] == [tx.id]


def test_rollback_pre_commit_state_after_crash(b):
    validators = generate_validators([1] * 4)
    b.store_validator_set(1, [v['storage'] for v in validators])
    b.store_block(Block(height=1, transactions=[], app_hash='')._asdict())

    public_key = validators[0]['public_key']
    private_key = validators[0]['private_key']
    voter_keys = [v['private_key'] for v in validators]

    migration_election, votes = generate_election(b,
                                                  ChainMigrationElection,
                                                  public_key, private_key,
                                                  {},
                                                  voter_keys)

    total_votes = votes
    txs = [migration_election, *votes]

    new_validator = generate_validators([1])[0]
    validator_election, votes = generate_election(b,
                                                  ValidatorElection,
                                                  public_key, private_key,
                                                  new_validator['election'],
                                                  voter_keys)

    total_votes += votes
    txs += [validator_election, *votes]

    b.store_bulk_transactions(txs)
    b.store_abci_chain(2, 'new_chain')
    b.store_validator_set(2, [v['storage'] for v in validators])
    # TODO change to `4` when upgrading to Tendermint 0.22.4.
    b.store_validator_set(3, [new_validator['storage']])
    b.store_election(migration_election.id, 2, is_concluded=False)
    b.store_election(validator_election.id, 2, is_concluded=True)

    # no pre-commit state
    rollback(b)

    for tx in txs:
        assert b.get_transaction(tx.id)
    assert b.get_latest_abci_chain()
    assert len(b.get_validator_change()['validators']) == 1
    assert b.get_election(migration_election.id)
    assert b.get_election(validator_election.id)

    b.store_pre_commit_state({'height': 2, 'transactions': [tx.id for tx in txs]})

    rollback(b)

    for tx in txs:
        assert not b.get_transaction(tx.id)
    assert not b.get_latest_abci_chain()
    assert len(b.get_validator_change()['validators']) == 4
    assert len(b.get_validator_change(2)['validators']) == 4
    assert not b.get_election(migration_election.id)
    assert not b.get_election(validator_election.id)


def test_new_validator_set(b):
    node1 = {'public_key': {'type': 'ed25519-base64',
                            'value': 'FxjS2/8AFYoIUqF6AcePTc87qOT7e4WGgH+sGCpTUDQ='},
             'voting_power': 10}
    node1_new_power = {'public_key': {'value': '1718D2DBFF00158A0852A17A01C78F4DCF3BA8E4FB7B8586807FAC182A535034',
                                      'type': 'ed25519-base16'},
                       'power': 20}
    node2 = {'public_key': {'value': '1888A353B181715CA2554701D06C1665BC42C5D936C55EA9C5DBCBDB8B3F02A3',
                            'type': 'ed25519-base16'},
             'power': 10}

    validators = [node1]
    updates = [node1_new_power, node2]
    b.store_validator_set(1, validators)
    updated_validator_set = new_validator_set(b.get_validators(1), updates)

    updated_validators = []
    for u in updates:
        updated_validators.append({'public_key': {'type': 'ed25519-base64',
                                                  'value': public_key_to_base64(u['public_key']['value'])},
                                   'voting_power':  u['power']})

    assert updated_validator_set == updated_validators


def test_info_aborts_if_chain_is_not_synced(b):
    b.store_abci_chain(0, 'chain-XYZ', False)

    with pytest.raises(SystemExit):
        App(b).info(RequestInfo())


def test_check_tx_aborts_if_chain_is_not_synced(b):
    b.store_abci_chain(0, 'chain-XYZ', False)

    with pytest.raises(SystemExit):
        App(b).check_tx('some bytes')


def test_begin_aborts_if_chain_is_not_synced(b):
    b.store_abci_chain(0, 'chain-XYZ', False)

    with pytest.raises(SystemExit):
        App(b).info(RequestBeginBlock())


def test_deliver_tx_aborts_if_chain_is_not_synced(b):
    b.store_abci_chain(0, 'chain-XYZ', False)

    with pytest.raises(SystemExit):
        App(b).deliver_tx('some bytes')


def test_end_block_aborts_if_chain_is_not_synced(b):
    b.store_abci_chain(0, 'chain-XYZ', False)

    with pytest.raises(SystemExit):
        App(b).info(RequestEndBlock())


def test_commit_aborts_if_chain_is_not_synced(b):
    b.store_abci_chain(0, 'chain-XYZ', False)

    with pytest.raises(SystemExit):
        App(b).commit()
