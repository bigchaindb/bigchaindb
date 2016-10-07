import rethinkdb as r

from bigchaindb_common.exceptions import AssetIdMismatch, AmountError


def get_asset_id(transactions):
    """Get the asset id from a list of transaction ids.

    This is useful when we want to check if the multiple inputs of a transaction
    are related to the same asset id.

    Args:
        transactions (list): list of transaction usually inputs that should have a matching asset_id

    Returns:
        str: uuid of the asset.

    Raises:
        AssetIdMismatch: If the inputs are related to different assets.
    """

    if not isinstance(transactions, list):
        transactions = [transactions]

    # create a set of asset_ids
    asset_ids = {tx['transaction']['asset']['id'] for tx in transactions}

    # check that all the transasctions have the same asset_id
    if len(asset_ids) > 1:
        raise AssetIdMismatch("All inputs of a transaction need to have the same asset id.")
    return asset_ids.pop()


def get_transactions_by_asset_id(asset_id, bigchain, read_mode='majority'):
    cursor = r.table('bigchain', read_mode=read_mode)\
              .get_all(asset_id, index='asset_id')\
              .concat_map(lambda block: block['block']['transactions'])\
              .filter(lambda transaction: transaction['transaction']['asset']['id'] == asset_id)\
              .run(bigchain.conn)

    transactions = list(cursor)
    return transactions
