from bigchaindb.migrations.migration_election import MigrationElection


def test_valid_migration_election(b_mock, node_key):
    voters = MigrationElection.recipients(b_mock)
    election = MigrationElection.generate([node_key.public_key],
                                          voters,
                                          {}, None).sign([node_key.private_key])
    assert election.validate(b_mock)
