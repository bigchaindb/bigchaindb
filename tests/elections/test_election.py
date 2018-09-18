import pytest

from tests.utils import generate_election, generate_validators

from bigchaindb.lib import Block
from bigchaindb.elections.election import Election
from bigchaindb.migrations.chain_migration_election import ChainMigrationElection
from bigchaindb.upsert_validator.validator_election import ValidatorElection


@pytest.mark.bdb
def test_approved_elections_concludes_all_elections(b):
    validators = generate_validators([1] * 4)
    b.store_validator_set(1, [v['storage'] for v in validators])

    new_validator = generate_validators([1])[0]

    public_key = validators[0]['public_key']
    private_key = validators[0]['private_key']
    election, votes = generate_election(b,
                                        ValidatorElection,
                                        public_key, private_key,
                                        new_validator['election'])
    txs = [election]
    total_votes = votes

    election, votes = generate_election(b,
                                        ChainMigrationElection,
                                        public_key, private_key,
                                        {})

    txs += [election]
    total_votes += votes

    b.store_abci_chain(1, 'chain-X')
    b.store_block(Block(height=1,
                        transactions=[tx.id for tx in txs],
                        app_hash='')._asdict())
    b.store_bulk_transactions(txs)

    Election.approved_elections(b, 1, total_votes)

    validators = b.get_validators()
    assert len(validators) == 5
    assert new_validator['storage'] in validators

    chain = b.get_latest_abci_chain()
    assert chain
    assert chain == {
        'height': 2,
        'is_synced': False,
        'chain_id': 'chain-X-migrated-at-height-1',
    }

    for tx in txs:
        election = b.get_election(tx.id)
        assert election


@pytest.mark.bdb
def test_approved_elections_applies_only_one_validator_update(b):
    validators = generate_validators([1] * 4)
    b.store_validator_set(1, [v['storage'] for v in validators])

    new_validator = generate_validators([1])[0]

    public_key = validators[0]['public_key']
    private_key = validators[0]['private_key']
    election, votes = generate_election(b,
                                        ValidatorElection,
                                        public_key, private_key,
                                        new_validator['election'])
    txs = [election]
    total_votes = votes

    another_validator = generate_validators([1])[0]

    election, votes = generate_election(b,
                                        ValidatorElection,
                                        public_key, private_key,
                                        another_validator['election'])
    txs += [election]
    total_votes += votes

    b.store_block(Block(height=1,
                        transactions=[tx.id for tx in txs],
                        app_hash='')._asdict())
    b.store_bulk_transactions(txs)

    Election.approved_elections(b, 1, total_votes)

    validators = b.get_validators()
    assert len(validators) == 5
    assert new_validator['storage'] in validators
    assert another_validator['storage'] not in validators

    assert b.get_election(txs[0].id)
    assert not b.get_election(txs[1].id)


@pytest.mark.bdb
def test_approved_elections_applies_only_one_migration(b):
    validators = generate_validators([1] * 4)
    b.store_validator_set(1, [v['storage'] for v in validators])

    public_key = validators[0]['public_key']
    private_key = validators[0]['private_key']
    election, votes = generate_election(b,
                                        ChainMigrationElection,
                                        public_key, private_key,
                                        {})
    txs = [election]
    total_votes = votes

    election, votes = generate_election(b,
                                        ChainMigrationElection,
                                        public_key, private_key,
                                        {})

    txs += [election]
    total_votes += votes

    b.store_abci_chain(1, 'chain-X')
    b.store_block(Block(height=1,
                        transactions=[tx.id for tx in txs],
                        app_hash='')._asdict())
    b.store_bulk_transactions(txs)

    Election.approved_elections(b, 1, total_votes)
    chain = b.get_latest_abci_chain()
    assert chain
    assert chain == {
        'height': 2,
        'is_synced': False,
        'chain_id': 'chain-X-migrated-at-height-1',
    }

    assert b.get_election(txs[0].id)
    assert not b.get_election(txs[1].id)


def test_approved_elections_gracefully_handles_empty_block(b):
    Election.approved_elections(b, 1, [])
