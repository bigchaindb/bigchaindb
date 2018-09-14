from unittest.mock import MagicMock

import pytest

from bigchaindb.elections.election import Election


@pytest.mark.bdb
def test_approved_elections_one_migration_one_upsert(
        b,
        ongoing_validator_election, validator_election_votes,
        ongoing_chain_migration_election, chain_migration_election_votes
):
    txns = validator_election_votes + \
           chain_migration_election_votes
    mock_chain_migration, mock_store_validator = run_approved_elections(b, txns)
    mock_chain_migration.assert_called_once()
    mock_store_validator.assert_called_once()


@pytest.mark.bdb
def test_approved_elections_one_migration_two_upsert(
        b,
        ongoing_validator_election, validator_election_votes,
        ongoing_validator_election_2, validator_election_votes_2,
        ongoing_chain_migration_election, chain_migration_election_votes
):
    txns = validator_election_votes + \
           validator_election_votes_2 + \
           chain_migration_election_votes
    mock_chain_migration, mock_store_validator = run_approved_elections(b, txns)
    mock_chain_migration.assert_called_once()
    mock_store_validator.assert_called_once()


@pytest.mark.bdb
def test_approved_elections_two_migrations_one_upsert(
        b,
        ongoing_validator_election, validator_election_votes,
        ongoing_chain_migration_election, chain_migration_election_votes,
        ongoing_chain_migration_election_2, chain_migration_election_votes_2
):
    txns = validator_election_votes + \
           chain_migration_election_votes + \
           chain_migration_election_votes_2
    mock_chain_migration, mock_store_validator = run_approved_elections(b, txns)
    assert mock_chain_migration.call_count == 2
    mock_store_validator.assert_called_once()


def test_approved_elections_no_elections(b):
    txns = []
    mock_chain_migration, mock_store_validator = run_approved_elections(b, txns)
    mock_chain_migration.assert_not_called()
    mock_store_validator.assert_not_called()


def run_approved_elections(bigchain, txns):
    mock_chain_migration = MagicMock()
    mock_store_validator = MagicMock()
    bigchain.migrate_abci_chain = mock_chain_migration
    bigchain.store_validator_set = mock_store_validator
    Election.approved_elections(bigchain, 1, txns)
    return mock_chain_migration, mock_store_validator
