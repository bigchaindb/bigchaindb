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
        return self.connection.run(
                r.table('bigchain', read_mode=self.read_mode)
                .get(block_id)
                .get_field('block')
                .get_field('transactions')
                .filter(lambda tx: tx['id'] == transaction_id))[0]

    def get_transaction_from_backlog(self, transaction_id):
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
        return self.connection.run(
                r.table('bigchain', read_mode=self.read_mode)
                .get_all(metadata_id, index='metadata_id')
                .concat_map(lambda block: block['block']['transactions'])
                .filter(lambda transaction: transaction['transaction']['metadata']['id'] == metadata_id))

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
        return self.connection.run(
            r.table('bigchain', read_mode=self.read_mode)
             .get_all(asset_id, index='asset_id')
             .concat_map(lambda block: block['block']['transactions'])
             .filter(lambda transaction: transaction['transaction']['asset']['id'] == asset_id))

    def get_spent(self, transaction_id, condition_id):
        return self.connection.run(
                r.table('bigchain', read_mode=self.read_mode)
                .concat_map(lambda doc: doc['block']['transactions'])
                .filter(lambda transaction: transaction['transaction']['fulfillments'].contains(
                    lambda fulfillment: fulfillment['input'] == {'txid': transaction_id, 'cid': condition_id})))

    def get_owned_ids(self, owner):
        return self.connection.run(
                r.table('bigchain', read_mode=self.read_mode)
                .concat_map(lambda doc: doc['block']['transactions'])
                .filter(lambda tx: tx['transaction']['conditions'].contains(
                    lambda c: c['owners_after'].contains(owner))))

    def get_votes_by_block_id(self, block_id):
        return self.connection.run(
                r.table('votes', read_mode=self.read_mode)
                .between([block_id, r.minval], [block_id, r.maxval], index='block_and_voter'))

    def get_votes_by_block_id_and_voter(self, block_id, node_pubkey):
        return self.connection.run(
                r.table('votes', read_mode=self.read_mode)
                .get_all([block_id, node_pubkey], index='block_and_voter'))

    def write_block(self, block, durability='soft'):
        return self.connection.run(
                r.table('bigchain')
                .insert(r.json(block), durability=durability))

    def has_transaction(self, transaction_id):
        return bool(self.connection.run(
                r.table('bigchain', read_mode=self.read_mode)
                .get_all(transaction_id, index='transaction_id').count()))

    def count_blocks(self):
        return self.connection.run(
                r.table('bigchain', read_mode=self.read_mode)
                .count())

    def write_vote(self, vote):
        return self.connection.run(
                r.table('votes')
                .insert(vote))

    def get_last_voted_block(self, node_pubkey):
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
            return self.connection.run(
                r.table('bigchain', read_mode=self.read_mode)
                .filter(util.is_genesis_block)
                .nth(0))

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
        """Return all the blocks that have not been voted on by this node.

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
