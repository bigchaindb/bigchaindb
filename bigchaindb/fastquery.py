from bigchaindb.utils import output_has_owner
from bigchaindb.backend import query
from bigchaindb.common.transaction import TransactionLink


class FastQuery:

    """
    Database queries that join on block results from a single node.

    * Votes are not validated for security (security is replication concern)
    * Votes come from only one node, and as such, fault tolerance is not provided
      (elected Blockchain table not yet available)

    In return, these queries offer good performance, as it is not neccesary to validate
    each result separately.
    """

    def __init__(self, connection, me):
        self.connection = connection
        self.me = me

    def filter_block_ids(self, block_ids, include_undecided=True):
        votes = query.get_votes_for_blocks_by_voter(
                    self.connection, block_ids, self.me)
        votes = {v['vote']['voting_for_block']: v['vote']['is_block_valid'] for v in votes}
        return [b for b in block_ids if votes.get(b, include_undecided)]

    def filter_valid_blocks(self, blocks):
        block_ids = list(set(b['id'] for b in blocks))
        valid_block_ids = self.filter_block_ids(block_ids)
        return [b for b in blocks if b['id'] in valid_block_ids]

    def get_outputs_by_pubkey(self, pubkey):
        cursor = query.get_owned_ids(self.connection, pubkey, unwrap=False)
        wrapped_txs = self.filter_valid_blocks(list(cursor))
        txs = [wrapped['block']['transactions'] for wrapped in wrapped_txs]
        return [TransactionLink(tx['id'], i)
                for tx in txs
                for i, o in enumerate(tx['outputs'])
                if output_has_owner(o, pubkey)]

    def filter_spent_outputs(self, outputs):
        """
        Remove outputs that have been spent

        Args:
            outputs: list of TransactionLink
        """
        links = [o.to_dict() for o in outputs]
        spending_txs = query.get_spending_transactions(self.connection, links)
        wrapped = self.filter_valid_blocks(list(spending_txs))
        spends = {TransactionLink.from_dict(input_['fulfills'])
                  for block in wrapped
                  for input_ in block['block']['transactions']['inputs']}
        return [ff for ff in outputs if ff not in spends]
