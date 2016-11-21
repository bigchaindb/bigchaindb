def validate_transaction_model(tx):
    from bigchaindb.common.transaction import Transaction
    from bigchaindb.common.schema import validate_transaction_schema

    tx_dict = tx.to_dict()
    # Check that a transaction is valid by re-serializing it
    # And calling validate_transaction_schema
    validate_transaction_schema(tx_dict)
    Transaction.from_dict(tx_dict)
