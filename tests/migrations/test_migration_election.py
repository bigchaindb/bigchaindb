from bigchaindb.migrations.chain_migration_election import ChainMigrationElection


def test_valid_migration_election(b_mock, node_key):
    voters = ChainMigrationElection.recipients(b_mock)
    election = ChainMigrationElection.generate([node_key.public_key],
                                               voters,
                                               {}, None).sign([node_key.private_key])
    assert election.validate(b_mock)
