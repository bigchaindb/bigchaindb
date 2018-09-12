import pytest

from bigchaindb.migrations.migration_election import MigrationElection


@pytest.fixture
def valid_migration_election(b_mock, node_key):
    voters = MigrationElection.recipients(b_mock)
    return MigrationElection.generate([node_key.public_key],
                                      voters,
                                      {}, None).sign([node_key.private_key])
