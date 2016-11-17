def validate_transaction_model(tx):
    from bigchaindb.common.transaction import Transaction
    # Check that a transaction is valid by re-serializing it
    Transaction.from_dict(tx.to_dict())
