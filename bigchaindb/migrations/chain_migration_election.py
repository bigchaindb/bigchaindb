from bigchaindb.common.schema import TX_SCHEMA_CHAIN_MIGRATION_ELECTION
from bigchaindb.elections.election import Election


class ChainMigrationElection(Election):

    OPERATION = 'CHAIN_MIGRATION_ELECTION'
    CREATE = OPERATION
    ALLOWED_OPERATIONS = (OPERATION,)
    TX_SCHEMA_CUSTOM = TX_SCHEMA_CHAIN_MIGRATION_ELECTION

    def has_concluded(self, bigchaindb, *args, **kwargs):
        chain = bigchaindb.get_latest_abci_chain()
        if chain is not None and not chain['is_synced']:
            # do not conclude the migration election if
            # there is another migration in progress
            return False

        return super().has_concluded(bigchaindb, *args, **kwargs)

    def on_approval(self, bigchain, *args, **kwargs):
        bigchain.migrate_abci_chain()
