"""Backend implementation for RethinkDB.

This module contains all the methods to store and retrieve data from RethinkDB.
"""

from time import time

import rethinkdb as r

from bigchaindb import util
from bigchaindb.db.utils import Connection
from bigchaindb.common import exceptions


class RethinkDBBackend:

    def __init__(self, host=None, port=None, db=None):
        """Initialize a new RethinkDB Backend instance.

        Args:
            host (str): the host to connect to.
            port (int): the port to connect to.
            db (str): the name of the database to use.
        """

        self.read_mode = 'majority'
        self.durability = 'soft'
        self.connection = Connection(host=host, port=port, db=db)

    def write_transaction(self, signed_transaction):
        """Write a transaction to the backlog table.

        Args:
            signed_transaction (dict): a signed transaction.

        Returns:
            The result of the operation.
        """

        return self.connection.run(
                r.table('backlog')
                .insert(signed_transaction, durability=self.durability))

    def update_transaction(self, transaction_id, doc):
        """Update a transaction in the backlog table.

        Args:
            transaction_id (str): the id of the transaction.
            doc (dict): the values to update.

        Returns:
            The result of the operation.
        """

        return self.connection.run(
                r.table('backlog')
                .get(transaction_id)
                .update(doc))

    def delete_transaction(self, *transaction_id):
        """Delete a transaction from the backlog.

        Args:
            *transaction_id (str): the transaction(s) to delete

        Returns:
            The database response.
        """

        return self.connection.run(
                r.table('backlog')
                .get_all(*transaction_id)
                .delete(durability='hard'))

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

        return self.connection.run(
                r.table('backlog')
                .filter(lambda tx: time() - tx['assignment_timestamp'] > reassign_delay))

    def get_transaction_from_block(self, transaction_id, block_id):
        """Get a transaction from a specific block.

        Args:
            transaction_id (str): the id of the transaction.
            block_id (str): the id of the block.

        Returns:
            The matching transaction.
        """
        return self.connection.run(
                r.table('bigchain', read_mode=self.read_mode)
                .get(block_id)
                .get_field('block')
                .get_field('transactions')
                .filter(lambda tx: tx['id'] == transaction_id))[0]

    def get_transaction_from_backlog(self, transaction_id):
        """Get a transaction from backlog.

        Args:
            transaction_id (str): the id of the transaction.

        Returns:
            The matching transaction.
        """
        return self.connection.run(
                r.table('backlog')
                .get(transaction_id)
                .without('assignee', 'assignment_timestamp')
                .default(None))

    def get_blocks_status_from_transaction(self, transaction_id):
        """Retrieve block election information given a secondary index and value

        Args:
            value: a value to search (e.g. transaction id string, payload hash string)
            index (str): name of a secondary index, e.g. 'transaction_id'

        Returns:
            :obj:`list` of :obj:`dict`: A list of blocks with with only election information
        """

        return self.connection.run(
                r.table('bigchain', read_mode=self.read_mode)
                .get_all(transaction_id, index='transaction_id')
                .pluck('votes', 'id', {'block': ['voters']}))

    def get_txids_by_metadata_id(self, metadata_id):
        """Retrieves transaction ids related to a particular metadata.

        When creating a transaction one of the optional arguments is the
        `metadata`. The metadata is a generic dict that contains extra
        information that can be appended to the transaction.

        To make it easy to query the bigchain for that particular metadata we
        create a UUID for the metadata and store it with the transaction.

        Args:
            metadata_id (str): the id for this particular metadata.

        Returns:
            A list of transaction ids containing that metadata. If no
            transaction exists with that metadata it returns an empty list `[]`
        """
        return self.connection.run(
                r.table('bigchain', read_mode=self.read_mode)
                .get_all(metadata_id, index='metadata_id')
                .concat_map(lambda block: block['block']['transactions'])
                .filter(lambda transaction:
                        transaction['transaction']['metadata']['id'] ==
                        metadata_id)
                .get_field('id'))

    def get_txids_by_asset_id(self, asset_id):
        """Retrieves transactions ids related to a particular asset.

        A digital asset in bigchaindb is identified by an uuid. This allows us
        to query all the transactions related to a particular digital asset,
        knowing the id.

        Args:
            asset_id (str): the id for this particular metadata.

        Returns:
            A list of transactions ids related to the asset. If no transaction
            exists for that asset it returns an empty list `[]`
        """

        # here we only want to return the transaction ids since later on when
        # we are going to retrieve the transaction with status validation
        return self.connection.run(
            r.table('bigchain', read_mode=self.read_mode)
             .get_all(asset_id, index='asset_id')
             .concat_map(lambda block: block['block']['transactions'])
             .filter(lambda transaction: transaction['transaction']['asset']['id'] == asset_id)
             .get_field('id'))

    def get_asset_by_id(self, asset_id):
        """Returns the asset associated with an asset_id.

            Args:
                asset_id (str): The asset id.

            Returns:
                Returns a rethinkdb cursor.
        """
        return self.connection.run(
            r.table('bigchain', read_mode=self.read_mode)
             .get_all(asset_id, index='asset_id')
             .concat_map(lambda block: block['block']['transactions'])
             .filter(lambda transaction:
                     transaction['transaction']['asset']['id'] == asset_id)
             .filter(lambda transaction:
                     transaction['transaction']['operation'] == 'CREATE')
             .pluck({'transaction': 'asset'}))

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

        # TODO: use index!
        return self.connection.run(
                r.table('bigchain', read_mode=self.read_mode)
                .concat_map(lambda doc: doc['block']['transactions'])
                .filter(lambda transaction: transaction['transaction']['fulfillments'].contains(
                    lambda fulfillment: fulfillment['input'] == {'txid': transaction_id, 'cid': condition_id})))

    def get_owned_ids(self, owner):
        """Retrieve a list of `txids` that can we used has inputs.

        Args:
            owner (str): base58 encoded public key.

        Returns:
            A cursor for the matching transactions.
        """

        # TODO: use index!
        return self.connection.run(
                r.table('bigchain', read_mode=self.read_mode)
                .concat_map(lambda doc: doc['block']['transactions'])
                .filter(lambda tx: tx['transaction']['conditions'].contains(
                    lambda c: c['owners_after'].contains(owner))))

    def get_votes_by_block_id(self, block_id):
        """Get all the votes casted for a specific block.

        Args:
            block_id (str): the block id to use.

        Returns:
            A cursor for the matching votes.
        """
        return self.connection.run(
                r.table('votes', read_mode=self.read_mode)
                .between([block_id, r.minval], [block_id, r.maxval], index='block_and_voter'))

    def get_votes_by_block_id_and_voter(self, block_id, node_pubkey):
        """Get all the votes casted for a specific block by a specific voter.

        Args:
            block_id (str): the block id to use.
            node_pubkey (str): base58 encoded public key

        Returns:
            A cursor for the matching votes.
        """
        return self.connection.run(
                r.table('votes', read_mode=self.read_mode)
                .get_all([block_id, node_pubkey], index='block_and_voter'))

    def write_block(self, block, durability='soft'):
        """Write a block to the bigchain table.

        Args:
            block (dict): the block to write.

        Returns:
            The database response.
        """
        return self.connection.run(
                r.table('bigchain')
                .insert(r.json(block), durability=durability))

    def get_block(self, block_id):
        """Get a block from the bigchain table

        Args:
            block_id (str): block id of the block to get

        Returns:
            block (dict): the block or `None`
        """
        return self.connection.run(r.table('bigchain').get(block_id))

    def has_transaction(self, transaction_id):
        """Check if a transaction exists in the bigchain table.

        Args:
            transaction_id (str): the id of the transaction to check.

        Returns:
            ``True`` if the transaction exists, ``False`` otherwise.
        """
        return bool(self.connection.run(
                r.table('bigchain', read_mode=self.read_mode)
                .get_all(transaction_id, index='transaction_id').count()))

    def count_blocks(self):
        """Count the number of blocks in the bigchain table.

        Returns:
            The number of blocks.
        """

        return self.connection.run(
                r.table('bigchain', read_mode=self.read_mode)
                .count())

    def count_backlog(self):
        """Count the number of transactions in the backlog table.

        Returns:
            The number of transactions in the backlog.
        """

        return self.connection.run(
                r.table('backlog', read_mode=self.read_mode)
                .count())

    def write_vote(self, vote):
        """Write a vote to the votes table.

        Args:
            vote (dict): the vote to write.

        Returns:
            The database response.
        """
        return self.connection.run(
                r.table('votes')
                .insert(vote))

    def get_genesis_block(self):
        """Get the genesis block

        Returns:
            The genesis block
        """
        return self.connection.run(
            r.table('bigchain', read_mode=self.read_mode)
            .filter(util.is_genesis_block)
            .nth(0))

    def get_last_voted_block(self, node_pubkey):
        """Get the last voted block for a specific node.

        Args:
            node_pubkey (str): base58 encoded public key.

        Returns:
            The last block the node has voted on. If the node didn't cast
            any vote then the genesis block is returned.
        """
        try:
            # get the latest value for the vote timestamp (over all votes)
            max_timestamp = self.connection.run(
                    r.table('votes', read_mode=self.read_mode)
                    .filter(r.row['node_pubkey'] == node_pubkey)
                    .max(r.row['vote']['timestamp']))['vote']['timestamp']

            last_voted = list(self.connection.run(
                r.table('votes', read_mode=self.read_mode)
                .filter(r.row['vote']['timestamp'] == max_timestamp)
                .filter(r.row['node_pubkey'] == node_pubkey)))

        except r.ReqlNonExistenceError:
            # return last vote if last vote exists else return Genesis block
            return self.get_genesis_block()

        # Now the fun starts. Since the resolution of timestamp is a second,
        # we might have more than one vote per timestamp. If this is the case
        # then we need to rebuild the chain for the blocks that have been retrieved
        # to get the last one.

        # Given a block_id, mapping returns the id of the block pointing at it.
        mapping = {v['vote']['previous_block']: v['vote']['voting_for_block']
                   for v in last_voted}

        # Since we follow the chain backwards, we can start from a random
        # point of the chain and "move up" from it.
        last_block_id = list(mapping.values())[0]

        # We must be sure to break the infinite loop. This happens when:
        # - the block we are currenty iterating is the one we are looking for.
        #   This will trigger a KeyError, breaking the loop
        # - we are visiting again a node we already explored, hence there is
        #   a loop. This might happen if a vote points both `previous_block`
        #   and `voting_for_block` to the same `block_id`
        explored = set()

        while True:
            try:
                if last_block_id in explored:
                    raise exceptions.CyclicBlockchainError()
                explored.add(last_block_id)
                last_block_id = mapping[last_block_id]
            except KeyError:
                break

        return self.connection.run(
                r.table('bigchain', read_mode=self.read_mode)
                .get(last_block_id))

    def get_unvoted_blocks(self, node_pubkey):
        """Return all the blocks that have not been voted by the specified node.

        Args:
            node_pubkey (str): base58 encoded public key

        Returns:
            :obj:`list` of :obj:`dict`: a list of unvoted blocks
        """

        unvoted = self.connection.run(
                r.table('bigchain', read_mode=self.read_mode)
                .filter(lambda block: r.table('votes', read_mode=self.read_mode)
                                       .get_all([block['id'], node_pubkey], index='block_and_voter')
                                       .is_empty())
                .order_by(r.asc(r.row['block']['timestamp'])))

        # FIXME: I (@vrde) don't like this solution. Filtering should be done at a
        #        database level. Solving issue #444 can help untangling the situation
        unvoted_blocks = filter(lambda block: not util.is_genesis_block(block), unvoted)
        return unvoted_blocks
