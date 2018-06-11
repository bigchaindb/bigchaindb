from bigchaindb.utils import condition_details_has_owner
from bigchaindb.backend import query
from bigchaindb.common.transaction import TransactionLink


class FastQuery:
    """Database queries that join on block results from a single node.

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

    def __init__(self, connection):
        self.connection = connection

    def get_outputs_by_public_key(self, public_key):
        """Get outputs for a public key"""
        res = list(query.get_owned_ids(self.connection, public_key))
        txs = [tx for _, tx in self.filter_valid_items(res)]
        return [TransactionLink(tx['id'], index)
                for tx in txs
                for index, output in enumerate(tx['outputs'])
                if condition_details_has_owner(output['condition']['details'],
                                               public_key)]

    def filter_spent_outputs(self, outputs):
        """Remove outputs that have been spent

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
        """Remove outputs that have not been spent

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
