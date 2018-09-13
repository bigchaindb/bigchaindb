from unittest.mock import MagicMock

import pytest

from bigchaindb.elections.election import Election


@pytest.mark.bdb
def test_approved_elections_one_migration_one_upsert(b,
                                                     ongoing_validator_election, validator_election_votes,
                                                     ongoing_migration_election, migration_election_votes):
    txns = validator_election_votes + \
           migration_election_votes
    mock_chain_migration, mock_store_validator = run_approved_elections(b, txns)
    mock_chain_migration.assert_called_once()
    mock_store_validator.assert_called_once()


@pytest.mark.bdb
def test_approved_elections_two_migrations_two_upsert(b,
                                                      ongoing_validator_election, validator_election_votes,
                                                      ongoing_validator_election_2, validator_election_votes_2,
                                                      ongoing_migration_election, migration_election_votes,
                                                      ongoing_migration_election_2, migration_election_votes_2):
    txns = validator_election_votes + \
           validator_election_votes_2 + \
           migration_election_votes + \
           migration_election_votes_2
    mock_chain_migration, mock_store_validator = run_approved_elections(b, txns)
    mock_chain_migration.assert_called_once()
    mock_store_validator.assert_called_once()


@pytest.mark.bdb
def test_approved_elections_two_migrations_one_upsert(b,
                                                      ongoing_validator_election, validator_election_votes,
                                                      ongoing_migration_election, migration_election_votes,
                                                      ongoing_migration_election_2, migration_election_votes_2):
    txns = validator_election_votes + \
           migration_election_votes + \
           migration_election_votes_2
    mock_chain_migration, mock_store_validator = run_approved_elections(b, txns)
    mock_chain_migration.assert_called_once()
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
