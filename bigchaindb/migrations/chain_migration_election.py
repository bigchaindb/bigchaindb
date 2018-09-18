from bigchaindb.common.schema import TX_SCHEMA_CHAIN_MIGRATION_ELECTION
from bigchaindb.elections.election import Election


class ChainMigrationElection(Election):

    OPERATION = 'CHAIN_MIGRATION_ELECTION'
    CREATE = OPERATION
    ALLOWED_OPERATIONS = (OPERATION,)
    TX_SCHEMA_CUSTOM = TX_SCHEMA_CHAIN_MIGRATION_ELECTION
    CHANGES_VALIDATOR_SET = False

    def has_concluded(self, bigchaindb, *args, **kwargs):
        chain = bigchaindb.get_latest_abci_chain()
        if chain is not None and not chain['is_synced']:
            # do not conclude the migration election if
            # there is another migration in progress
            return False

        return super().has_concluded(bigchaindb, *args, **kwargs)

    @classmethod
    def on_approval(cls, bigchain, election, new_height):
        bigchain.migrate_abci_chain()
