from bigchaindb.common.exceptions import ValidationError


def is_clean_script(script):
    if 'bigchain.' in script:
        if 'bigchain.get_' not in script:
            return False
    if 'while' in script:
        return False
    # if 'for' in script:
    #     return False
    if 'wait' in script:
        return False
    return True


def validate_asset(transaction, bigchain):
    if not hasattr(transaction, 'asset'):
        raise ValidationError('Asset not found in transaction {}'.format(transaction))

    asset = transaction.asset
    if not asset:
        return transaction

    if 'id' in asset:
        create_tx = bigchain.get_transaction(asset['id'])
        asset = create_tx.asset

    asset_data = asset['data']

    if asset_data and 'script' in asset_data:
        script = asset_data['script']

        if not is_clean_script(script):
            raise ValidationError('Asset script might contain malicious code:\n{}'.format(script))

        try:
            # do not allow builtins or other funky business
            context = {
                'print': print,
                'len': len
            }

            exec(script, {"__builtins__": context}, {'bigchain': bigchain, 'self': transaction})
            return transaction

        except Exception as e:
            raise ValidationError('Asset script evaluation failed with {} : {}'
                                  .format(e.__class__.__name__, e).rstrip())
    else:
        # No script, asset is always valid
        return transaction
