import rethinkdb as r

from bigchaindb.exceptions import AssetIdMismatch, AmountError


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


def validate_asset_creation(asset_data, divisible, updatable, refillable, amount):
    """Validate digital asset

    Args:
        asset_data (dict or None): dictionary describing the digital asset (only used on a create transaction)
        divisible (boolean): Whether the asset is divisible or not. Defaults to `False`.
        updatable (boolean): Whether the data in the asset can be updated in the future or not.
                                       Defaults to `False`.
        refillable (boolean): Whether the amount of the asset can change after its creation.
                                        Defaults to `False`.
        amount (int): The amount of "shares". Only relevant if the asset is marked as divisible.
                                Defaults to `1`.
    """
    if asset_data is not None and not isinstance(asset_data, dict):
        raise TypeError('`data` must be a dict instance or None')
    if not isinstance(divisible, bool):
        raise TypeError('`divisible` must be a boolean')
    if not isinstance(refillable, bool):
        raise TypeError('`refillable` must be a boolean')
    if not isinstance(updatable, bool):
        raise TypeError('`updatable` must be a boolean')
    if not isinstance(amount, int):
        raise TypeError('`amount` must be an int')
    if divisible is False and amount != 1:
        raise AmountError('Non-divisible assets must have amount 1')
    if amount < 1:
        raise AmountError('The amount cannot be less then 1')

    if divisible or updatable or refillable or amount != 1:
        raise NotImplementedError("Divisible assets are not yet implemented!")


def get_transactions_by_asset_id(asset_id, bigchain, read_mode='majority'):
    cursor = r.table('bigchain', read_mode=read_mode)\
              .get_all(asset_id, index='asset_id')\
              .concat_map(lambda block: block['block']['transactions'])\
              .filter(lambda transaction: transaction['transaction']['asset']['id'] == asset_id)\
              .run(bigchain.conn)

    transactions = list(cursor)
    return transactions
