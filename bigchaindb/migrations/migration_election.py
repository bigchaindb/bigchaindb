from bigchaindb.common.schema import TX_SCHEMA_MIGRATION_ELECTION
from bigchaindb.elections.election import Election


class MigrationElection(Election):

    OPERATION = 'MIGRATION_ELECTION'
    CREATE = OPERATION
    ALLOWED_OPERATIONS = (OPERATION,)
    TX_SCHEMA_CUSTOM = TX_SCHEMA_MIGRATION_ELECTION

    @classmethod
    def on_approval(cls, bigchain, election, new_height):
        bigchain.migrate_abci_chain()
