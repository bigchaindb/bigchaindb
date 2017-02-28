"""Module to store messages used in commands, such as error messages,
warnings, prompts, etc.

"""
CANNOT_START_KEYPAIR_NOT_FOUND = (
    "Can't start BigchainDB, no keypair found. "
    'Did you run `bigchaindb configure`?'
)

RETHINKDB_STARTUP_ERROR = 'Error starting RethinkDB, reason is: {}'
