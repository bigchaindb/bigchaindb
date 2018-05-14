"""Query interfaces for backends."""

from functools import singledispatch

from bigchaindb.backend.exceptions import OperationError

VALIDATOR_UPDATE_ID = 'a_unique_id_string'
PRE_COMMIT_ID = 'a_unique_id_string'


@singledispatch
def store_transaction(connection, signed_transaction):
    """Write a transaction to the backlog table.

    Args:
        signed_transaction (dict): a signed transaction.

    Returns:
        The result of the operation.
    """

    raise NotImplementedError


@singledispatch
def store_asset(connection, asset):
    """Write an asset to the asset table.

    Args:
        asset (dict): the asset.

    Returns:
        The result of the operation.
    """

    raise NotImplementedError


@singledispatch
def store_assets(connection, assets):
    """Write a list of assets to the assets table.

    Args:
        assets (list): a list of assets to write.

    Returns:
        The database response.
    """

    raise NotImplementedError


@singledispatch
def store_metadatas(connection, metadata):
    """Write a list of metadata to metadata table.

    Args:
        metadata (list): list of metadata.

    Returns:
        The result of the operation.
    """

    raise NotImplementedError


@singledispatch
def store_transactions(connection, signed_transactions):
    """Store the list of transactions."""

    raise NotImplementedError


@singledispatch
def get_transaction(connection, transaction_id):
    """Get a transaction from the transactions table.

    Args:
        transaction_id (str): the id of the transaction.

    Returns:
        The result of the operation.
    """

    raise NotImplementedError


@singledispatch
def get_transactions(connection, transaction_ids):
    """Get transactions from the transactions table.

    Args:
        transaction_ids (list): list of transaction ids to fetch

    Returns:
        The result of the operation.
    """

    raise NotImplementedError


@singledispatch
def get_asset(connection, asset_id):
    """Get a transaction from the transactions table.

    Args:
        asset_id (str): the id of the asset

    Returns:
        The result of the operation.
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
def get_spending_transactions(connection, inputs):
    """Return transactions which spend given inputs

    Args:
        inputs (list): list of {txid, output}

    Returns:
        Iterator of (block_ids, transaction) for transactions that
        spend given inputs.
    """
    raise NotImplementedError


@singledispatch
def get_owned_ids(connection, owner):
    """Retrieve a list of `txids` that can we used has inputs.

    Args:
        owner (str): base58 encoded public key.

    Returns:
        Iterator of (block_id, transaction) for transactions
        that list given owner in conditions.
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
def get_block_with_transaction(connection, txid):
    """Get a block containing transaction id `txid`

    Args:
        txid (str): id of transaction to be searched.

    Returns:
        block_id (int): the block id or `None`
    """

    raise NotImplementedError


@singledispatch
def get_metadata(connection, transaction_ids):
    """Get a list of metadata from the metadata table.

    Args:
        transaction_ids (list): a list of ids for the metadata to be retrieved from
        the database.

    Returns:
        metadata (list): the list of returned metadata.
    """
    raise NotImplementedError


@singledispatch
def get_assets(connection, asset_ids):
    """Get a list of assets from the assets table.
    Args:
        asset_ids (list): a list of ids for the assets to be retrieved from
        the database.
    Returns:
        assets (list): the list of returned assets.
    """
    raise NotImplementedError


@singledispatch
def get_txids_filtered(connection, asset_id, operation=None):
    """Return all transactions for a particular asset id and optional operation.

    Args:
        asset_id (str): ID of transaction that defined the asset
        operation (str) (optional): Operation to filter on
    """

    raise NotImplementedError


@singledispatch
def text_search(conn, search, *, language='english', case_sensitive=False,
                diacritic_sensitive=False, text_score=False, limit=0, table=None):
    """Return all the assets that match the text search.

    The results are sorted by text score.
    For more information about the behavior of text search on MongoDB see
    https://docs.mongodb.com/manual/reference/operator/query/text/#behavior

    Args:
        search (str): Text search string to query the text index
        language (str, optional): The language for the search and the rules for
            stemmer and tokenizer. If the language is ``None`` text search uses
            simple tokenization and no stemming.
        case_sensitive (bool, optional): Enable or disable case sensitive
            search.
        diacritic_sensitive (bool, optional): Enable or disable case sensitive
            diacritic search.
        text_score (bool, optional): If ``True`` returns the text score with
            each document.
        limit (int, optional): Limit the number of returned documents.

    Returns:
        :obj:`list` of :obj:`dict`: a list of assets

    Raises:
        OperationError: If the backend does not support text search
    """

    raise OperationError('This query is only supported when running '
                         'BigchainDB with MongoDB as the backend.')


@singledispatch
def get_latest_block(conn):
    """Get the latest commited block i.e. block with largest height"""

    raise NotImplementedError


@singledispatch
def store_block(conn, block):
    """Write a new block to the `blocks` table

    Args:
        block (dict): block with current height and block hash.

    Returns:
        The result of the operation.
    """

    raise NotImplementedError


@singledispatch
def store_unspent_outputs(connection, unspent_outputs):
    """Store unspent outputs in ``utxo_set`` table."""

    raise NotImplementedError


@singledispatch
def delete_unspent_outputs(connection, unspent_outputs):
    """Delete unspent outputs in ``utxo_set`` table."""

    raise NotImplementedError


@singledispatch
def delete_transactions(conn, txn_ids):
    """Delete transactions from database

    Args:
        txn_ids (list): list of transaction ids

    Returns:
        The result of the operation.
    """

    raise NotImplementedError


@singledispatch
def get_unspent_outputs(connection, *, query=None):
    """Retrieves unspent outputs.

    Args:
        query (dict): An optional parameter to filter the result set.
            Defaults to ``None``, which means that all UTXO records
            will be returned.

    Returns:
        Generator yielding unspent outputs (UTXO set) according to the
        given query.
    """

    raise NotImplementedError


@singledispatch
def store_pre_commit_state(connection, commit_id, state):
    """Store pre-commit state in a document with `id` as `commit_id`.

    Args:
        commit_id (string): `id` of document where `state` should be stored.
        state (dict): commit state.

    Returns:
        The result of the operation.
    """

    raise NotImplementedError


@singledispatch
def store_validator_update(conn, validator_update):
    """Store a update for the validator set"""

    raise NotImplementedError


@singledispatch
def get_pre_commit_state(connection, commit_id):
    """Get pre-commit state where `id` is `commit_id`.

    Args:
        commit_id (string): `id` of document where `state` should be stored.

    Returns:
        Document with `id` as `commit_id`
    """

    raise NotImplementedError


@singledispatch
def get_validator_update(conn):
    """Get validator updates which are not synced"""

    raise NotImplementedError


@singledispatch
def delete_validator_update(conn, id):
    """Set the sync status for validator update documents"""

    raise NotImplementedError
