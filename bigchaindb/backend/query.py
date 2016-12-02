
"""Interface to query the database.

This module contains all the methods to store and retrieve data from a generic database.
"""


class Query:

    def write_transaction(self, signed_transaction):
        """Write a transaction to the backlog table.

        Args:
            signed_transaction (dict): a signed transaction.

        Returns:
            The result of the operation.
        """
        raise NotImplementedError()

    def update_transaction(self, transaction_id, doc):
        """Update a transaction in the backlog table.

        Args:
            transaction_id (str): the id of the transaction.
            doc (dict): the values to update.

        Returns:
            The result of the operation.
        """
        raise NotImplementedError()

    def delete_transaction(self, *transaction_id):
        """Delete a transaction from the backlog.

        Args:
            *transaction_id (str): the transaction(s) to delete

        Returns:
            The database response.
        """
        raise NotImplementedError()

    def get_stale_transactions(self, reassign_delay):
        """Get a cursor of stale transactions.

        Transactions are considered stale if they have been assigned a node,
        but are still in the backlog after some amount of time specified in the
        configuration.

        Args:
            reassign_delay (int): threshold (in seconds) to mark a transaction stale.

        Returns:
            A cursor of transactions.
        """

        raise NotImplementedError()

    def get_transaction_from_block(self, transaction_id, block_id):
        """Get a transaction from a specific block.

        Args:
            transaction_id (str): the id of the transaction.
            block_id (str): the id of the block.

        Returns:
            The matching transaction.
        """

        raise NotImplementedError()

    def get_transaction_from_backlog(self, transaction_id):
        """Get a transaction from backlog.

        Args:
            transaction_id (str): the id of the transaction.

        Returns:
            The matching transaction.
        """

        raise NotImplementedError()

    def get_blocks_status_from_transaction(self, transaction_id):
        """Retrieve block election information given a secondary index and value

        Args:
            value: a value to search (e.g. transaction id string, payload hash string)
            index (str): name of a secondary index, e.g. 'transaction_id'

        Returns:
            :obj:`list` of :obj:`dict`: A list of blocks with with only election information
        """

        raise NotImplementedError()

    def get_transactions_by_metadata_id(self, metadata_id):
        """Retrieves transactions related to a metadata.

        When creating a transaction one of the optional arguments is the `metadata`. The metadata is a generic
        dict that contains extra information that can be appended to the transaction.

        To make it easy to query the bigchain for that particular metadata we create a UUID for the metadata and
        store it with the transaction.

        Args:
            metadata_id (str): the id for this particular metadata.

        Returns:
            A list of transactions containing that metadata. If no transaction exists with that metadata it
            returns an empty list `[]`
        """

        raise NotImplementedError()

    def get_transactions_by_asset_id(self, asset_id):
        """Retrieves transactions related to a particular asset.

        A digital asset in bigchaindb is identified by an uuid. This allows us to query all the transactions
        related to a particular digital asset, knowing the id.

        Args:
            asset_id (str): the id for this particular metadata.

        Returns:
            A list of transactions containing related to the asset. If no transaction exists for that asset it
            returns an empty list `[]`
        """

        raise NotImplementedError()

    def get_spent(self, transaction_id, condition_id):
        """Check if a `txid` was already used as an input.

        A transaction can be used as an input for another transaction. Bigchain needs to make sure that a
        given `txid` is only used once.

        Args:
            transaction_id (str): The id of the transaction.
            condition_id (int): The index of the condition in the respective transaction.

        Returns:
            The transaction that used the `txid` as an input else `None`
        """

        raise NotImplementedError()

    def get_owned_ids(self, owner):
        """Retrieve a list of `txids` that can we used has inputs.

        Args:
            owner (str): base58 encoded public key.

        Returns:
            A cursor for the matching transactions.
        """

        raise NotImplementedError()

    def get_votes_by_block_id(self, block_id):
        """Get all the votes casted for a specific block.

        Args:
            block_id (str): the block id to use.

        Returns:
            A cursor for the matching votes.
        """

        raise NotImplementedError()

    def get_votes_by_block_id_and_voter(self, block_id, node_pubkey):
        """Get all the votes casted for a specific block by a specific voter.

        Args:
            block_id (str): the block id to use.
            node_pubkey (str): base58 encoded public key

        Returns:
            A cursor for the matching votes.
        """

        raise NotImplementedError()

    def write_block(self, block, durability='soft'):
        """Write a block to the bigchain table.

        Args:
            block (dict): the block to write.

        Returns:
            The database response.
        """

        raise NotImplementedError()

    def has_transaction(self, transaction_id):
        """Check if a transaction exists in the bigchain table.

        Args:
            transaction_id (str): the id of the transaction to check.

        Returns:
            ``True`` if the transaction exists, ``False`` otherwise.
        """

        raise NotImplementedError()

    def count_blocks(self):
        """Count the number of blocks in the bigchain table.

        Returns:
            The number of blocks.
        """

        raise NotImplementedError()

    def write_vote(self, vote):
        """Write a vote to the votes table.

        Args:
            vote (dict): the vote to write.

        Returns:
            The database response.
        """

        raise NotImplementedError()

    def get_last_voted_block(self, node_pubkey):
        """Get the last voted block for a specific node.

        Args:
            node_pubkey (str): base58 encoded public key.

        Returns:
            The last block the node has voted on. If the node didn't cast
            any vote then the genesis block is returned.
        """

        raise NotImplementedError()

    def get_unvoted_blocks(self, node_pubkey):
        """Return all the blocks that have not been voted by the specified node.

        Args:
            node_pubkey (str): base58 encoded public key

        Returns:
            :obj:`list` of :obj:`dict`: a list of unvoted blocks
        """

        raise NotImplementedError()
