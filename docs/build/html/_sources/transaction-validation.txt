# Transaction Validation

## Generic Validation

1. Query the bigchain and check if `current_owner` actually owns the `hash`.
2. Check if the transaction was signed with `current_owner` private key.

## Specific Validation

1. Query the bigchain and check if `current_owner` actually owns the `hash`.
2. Check if the transaction was signed with `current_owner` private key.
3. Depending on the `operation` additional checks may need to be performed. This will be specified by the protocol 
running in the chain e. g. [Spool protocol](https://github.com/ascribe/spool)