from bigchaindb.utils import condition_details_has_owner
from bigchaindb.backend import query
from bigchaindb.common.transaction import TransactionLink


class FastQuery:
    """
    Database queries that join on block results from a single node.

    * Votes are not validated for security (security is a replication concern)
    * Votes come from only one node, and as such, non-byzantine fault tolerance
      is reduced.

    Previously, to consider the status of a block, all votes for that block
    were retrieved and the election results were counted. This meant that a
    faulty node may still have been able to obtain a correct election result.
    However, from the point of view of a client, it is still neccesary to
    query multiple nodes to insure against getting an incorrect response from
    a byzantine node.
    """
    def __init__(self, connection, me):
        self.connection = connection
        self.me = me

    def filter_valid_block_ids(self, block_ids, include_undecided=False):
        """
        Given block ids, return only the ones that are valid.
        """
        block_ids = list(set(block_ids))
        votes = query.get_votes_for_blocks_by_voter(
                    self.connection, block_ids, self.me)
        votes = {vote['vote']['voting_for_block']: vote['vote']['is_block_valid']
                 for vote in votes}
        return [block_id for block_id in block_ids
                if votes.get(block_id, include_undecided)]

    def filter_valid_items(self, items, block_id_key=lambda b: b[0]):
        """
        Given items with block ids, return only the ones that are valid or undecided.
        """
        items = list(items)
        block_ids = map(block_id_key, items)
        valid_block_ids = set(self.filter_valid_block_ids(block_ids, True))
        return [b for b in items if block_id_key(b) in valid_block_ids]

    def get_outputs_by_public_key(self, public_key):
        """
        Get outputs for a public key
        """
        res = list(query.get_owned_ids(self.connection, public_key))
        txs = [tx for _, tx in self.filter_valid_items(res)]
        return [TransactionLink(tx['id'], index)
                for tx in txs
                for index, output in enumerate(tx['outputs'])
                if condition_details_has_owner(output['condition']['details'],
                                               public_key)]

    def filter_spent_outputs(self, outputs):
        """
        Remove outputs that have been spent

        Args:
            outputs: list of TransactionLink
        """
        links = [o.to_dict() for o in outputs]
        res = query.get_spending_transactions(self.connection, links)
        txs = [tx for _, tx in self.filter_valid_items(res)]
        spends = {TransactionLink.from_dict(input_['fulfills'])
                  for tx in txs
                  for input_ in tx['inputs']}
        return [ff for ff in outputs if ff not in spends]

    def filter_unspent_outputs(self, outputs):
        """
        Remove outputs that have not been spent

        Args:
            outputs: list of TransactionLink
        """
        links = [o.to_dict() for o in outputs]
        res = query.get_spending_transactions(self.connection, links)
        txs = [tx for _, tx in self.filter_valid_items(res)]
        spends = {TransactionLink.from_dict(input_['fulfills'])
                  for tx in txs
                  for input_ in tx['inputs']}
        return [ff for ff in outputs if ff in spends]
