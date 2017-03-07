import pytest
from bigchaindb.common import exceptions as exc
from bigchaindb.models import Transaction


################################################################################
# 1.1 - The asset ID of a CREATE transaction is the same as it's ID


def test_create_tx_no_asset_id(b):
    tx = Transaction.create([b.me], [([b.me], 1)])
    # works
    Transaction.validate_structure(tx.to_dict())
    # broken
    tx.asset['id'] = 'b' * 64
    with pytest.raises(exc.SchemaValidationError):
        Transaction.validate_structure(tx.to_dict())
