"""Query interfaces for backends."""

from functools import singledispatch


@singledispatch
def write_transaction(connection, signed_transaction):
    """Write a transaction to the backlog table.

    Args:
        signed_transaction (dict): a signed transaction.

    Returns:
        The result of the operation.
    """

    raise NotImplementedError


@singledispatch
def update_transaction(connection, transaction_id, doc):
    """Update a transaction in the backlog table.

    Args:
        transaction_id (str): the id of the transaction.
        doc (dict): the values to update.

    Returns:
        The result of the operation.
    """

    raise NotImplementedError


@singledispatch
def delete_transaction(connection, *transaction_id):
    """Delete a transaction from the backlog.

    Args:
        *transaction_id (str): the transaction(s) to delete.

    Returns:
        The database response.
    """
    raise NotImplementedError


@singledispatch
def get_stale_transactions(connection, reassign_delay):
    """Get a cursor of stale transactions.

    Transactions are considered stale if they have been assigned a node,
    but are still in the backlog after some amount of time specified in the
    configuration.

    Args:
        reassign_delay (int): threshold (in seconds) to mark a transaction stale.

    Returns:
        A cursor of transactions.
    """

    raise NotImplementedError


@singledispatch
def get_transaction_from_block(connection, transaction_id, block_id):
    """Get a transaction from a specific block.

    Args:
        transaction_id (str): the id of the transaction.
        block_id (str): the id of the block.

    Returns:
        The matching transaction.
    """

    raise NotImplementedError


@singledispatch
def get_transaction_from_backlog(connection, transaction_id):
    """Get a transaction from backlog.

    Args:
        transaction_id (str): the id of the transaction.

    Returns:
        The matching transaction.
    """

    raise NotImplementedError


@singledispatch
def get_blocks_status_from_transaction(connection, transaction_id):
    """Retrieve block election information given a secondary index and value.

    Args:
        value: a value to search (e.g. transaction id string, payload hash string)
        index (str): name of a secondary index, e.g. 'transaction_id'

    Returns:
        :obj:`list` of :obj:`dict`: A list of blocks with with only election information
    """

    raise NotImplementedError


@singledispatch
def get_asset_by_id(conneciton, asset_id):
    """Returns the asset associated with an asset_id.

    Args:
        asset_id (str): The asset id.

    Returns:
        Returns a rethinkdb cursor.
    """

    raise NotImplementedError


@singledispatch
def get_spent(connection, transaction_id, condition_id):
    """Check if a `txid` was already used as an input.

    A transaction can be used as an input for another transaction. Bigchain
    needs to make sure that a given `txid` is only used once.

    Args:
        transaction_id (str): The id of the transaction.
        condition_id (int): The index of the condition in the respective
            transaction.

    Returns:
        The transaction that used the `txid` as an input else `None`
    """

    raise NotImplementedError


@singledispatch
def get_owned_ids(connection, owner):
    """Retrieve a list of `txids` that can we used has inputs.

    Args:
        owner (str): base58 encoded public key.

    Returns:
        A cursor for the matching transactions.
    """

    raise NotImplementedError


@singledispatch
def get_votes_by_block_id(connection, block_id):
    """Get all the votes casted for a specific block.

    Args:
        block_id (str): the block id to use.

    Returns:
        A cursor for the matching votes.
    """

    raise NotImplementedError


@singledispatch
def get_votes_by_block_id_and_voter(connection, block_id, node_pubkey):
    """Get all the votes casted for a specific block by a specific voter.

    Args:
        block_id (str): the block id to use.
        node_pubkey (str): base58 encoded public key

    Returns:
        A cursor for the matching votes.
    """

    raise NotImplementedError


@singledispatch
def write_block(connection, block):
    """Write a block to the bigchain table.

    Args:
        block (dict): the block to write.

    Returns:
        The database response.
    """

    raise NotImplementedError


@singledispatch
def get_block(connection, block_id):
    """Get a block from the bigchain table.

    Args:
        block_id (str): block id of the block to get

    Returns:
        block (dict): the block or `None`
    """

    raise NotImplementedError


@singledispatch
def has_transaction(connection, transaction_id):
    """Check if a transaction exists in the bigchain table.

    Args:
        transaction_id (str): the id of the transaction to check.

    Returns:
        ``True`` if the transaction exists, ``False`` otherwise.
    """

    raise NotImplementedError


@singledispatch
def count_blocks(connection):
    """Count the number of blocks in the bigchain table.

    Returns:
        The number of blocks.
    """

    raise NotImplementedError


@singledispatch
def count_backlog(connection):
    """Count the number of transactions in the backlog table.

    Returns:
        The number of transactions in the backlog.
    """

    raise NotImplementedError


@singledispatch
def write_vote(connection, vote):
    """Write a vote to the votes table.

    Args:
        vote (dict): the vote to write.

    Returns:
        The database response.
    """

    raise NotImplementedError


@singledispatch
def get_genesis_block(connection):
    """Get the genesis block.

    Returns:
        The genesis block
    """

    raise NotImplementedError


@singledispatch
def get_last_voted_block(connection, node_pubkey):
    """Get the last voted block for a specific node.

    Args:
        node_pubkey (str): base58 encoded public key.

    Returns:
        The last block the node has voted on. If the node didn't cast
        any vote then the genesis block is returned.
    """

    raise NotImplementedError


@singledispatch
def get_unvoted_blocks(connection, node_pubkey):
    """Return all the blocks that have not been voted by the specified node.

    Args:
        node_pubkey (str): base58 encoded public key

    Returns:
        :obj:`list` of :obj:`dict`: a list of unvoted blocks
    """

    raise NotImplementedError


@singledispatch
def get_txids_filtered(connection, asset_id, operation=None):
    """
    Return all transactions for a particular asset id and optional operation.

    Args:
        asset_id (str): ID of transaction that defined the asset
        operation (str) (optional): Operation to filter on
    """

    raise NotImplementedError
