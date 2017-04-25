from bigchaindb.utils import output_has_owner
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

    def filter_block_ids(self, block_ids, include_undecided=True):
        """
        Given block ids, filter the invalid blocks.
        """
        block_ids = list(set(block_ids))
        votes = query.get_votes_for_blocks_by_voter(
                    self.connection, block_ids, self.me)
        votes = {v['vote']['voting_for_block']: v['vote']['is_block_valid'] for v in votes}
        return [b for b in block_ids if votes.get(b, include_undecided)]

    def filter_valid_blocks(self, blocks, key=lambda b: b[0]):
        """
        Given things with block ids, remove the invalid ones.
        """
        blocks = list(blocks)
        valid_block_ids = set(self.filter_block_ids(key(b) for b in blocks))
        return [b for b in blocks if key(b) in valid_block_ids]

    def get_outputs_by_pubkey(self, pubkey):
        """ Get outputs for a public key """
        res = list(query.get_owned_ids(self.connection, pubkey))
        txs = [tx for _, tx in self.filter_valid_blocks(res)]
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
        res = query.get_spending_transactions(self.connection, links)
        txs = [tx for _, tx in self.filter_valid_blocks(res)]
        spends = {TransactionLink.from_dict(input_['fulfills'])
                  for tx in txs
                  for input_ in tx['inputs']}
        return [ff for ff in outputs if ff not in spends]
