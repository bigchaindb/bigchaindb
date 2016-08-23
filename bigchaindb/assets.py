from bigchaindb.exceptions import AssetIdMismatch


def get_asset_id(txids, bigchain):
    """Get the asset id from a list of transaction ids.

    This is useful when we want to check if the multiple inputs of a transaction
    are related to the same asset id.

    Args:
        txids (list): list of transaction ids.

    Returns:
        str: uuid of the asset.

    Raises:
        AssetIdMismatch: If the inputs are related to different assets.
    """

    if not isinstance(txids, list):
        txids = [txids]

    asset_ids = []
    for txid in set(txids):
        tx = bigchain.get_transaction(txid)
        if tx['transaction']['operation'] == 'CREATE':
            asset_ids.append(tx['transaction']['asset']['id'])
        else:
            asset_ids.append(tx['transaction']['asset'])

    asset_ids = set(asset_ids)
    if len(asset_ids) > 1:
        raise AssetIdMismatch("All inputs of a transaction need to have the same asset id.")
    return asset_ids.pop()
