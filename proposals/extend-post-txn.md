## Feature : Add query parameter "mode" to `POST` transaction
Add new query paramter `mode` to the [post transaction api](https://docs.bigchaindb.com/projects/server/en/latest/http-client-server-api.html#post--api-v1-transactions) such that client can,
- asynchoronously post the transaction
- post the transaction and return after its validated
- post the transaction and return after its commited

## Problem Description
When posting a transaction it is broadcasted asynchoronously to tendermint which enables the client to return immediately. Furthermore, the transaction status api would allow the client to get the current status for a given transaction. The above workflow seems efficient when the client doesn't need to wait until a transaction gets commited. Incase a client wishes to wait until a transaction gets commited it would need to poll the transaction status api. 
The tendermint api allows to post a transaction in [three modes](http://tendermint.readthedocs.io/projects/tools/en/master/using-tendermint.html#broadcast-api),

- `/broadcast_tx_async` post transaction and return
- `/broadcast_tx_sync` post transaction and return after `checkTx` is executed
- `/broadcast_tx_commit` post transaction and return after the transaction has been committed

### Use cases
- allow clients to post a transaction synchronously i.e. the `POST` transaction request returns after the transaction has passed `checkTx`.
- allow client to post a transaction and return after a transaction has been commited.

## Proposed change
Add query paramter `mode` to the [`POST` transaction api](https://docs.bigchaindb.com/projects/server/en/latest/http-client-server-api.html#post--api-v1-transactions)

### Alternatives
N/A

### Data model impact
N/A

### API impact
The query parameter `mode` will be introduced to [`POST /api/v1/transaction`](https://docs.bigchaindb.com/projects/server/en/latest/http-client-server-api.html#post--api-v1-transactions) and will have the following possible values
- `async`
- `sync`
- `commit`

To preserve compability with the existing behavour of the api the default value of `mode` would be `async`.

example uri: `/api/v1/transaction?mode=async`

### Security impact
N/A

### Performance impact
N/A

### End user impact
The feature itself will not impact the client drivers but it may lead to [`GET /api/v1/statuses?transaction_id={transaction_id}`](https://docs.bigchaindb.com/projects/server/en/latest/http-client-server-api.html#get--api-v1-statuses?transaction_id=transaction_id) being depricated in the future.

### Deployment impact
N/A

### Documentation impact
The documentation for [posting a transaction](https://docs.bigchaindb.com/projects/server/en/latest/http-client-server-api.html#post--api-v1-transactions) would need to describe the use of query parameter `mode` 

### Testing impact
Following new test cases should be included
- `POST` a transaction with no `mode` i.e. `POST /api/v1/transaction`
- `POST` a transaction with `mode=sync`, `mode=async`, `mode=commit`
- `POST` a transaction with invalid `mode`

## Implementation

### Assignee(s)
Primary assignee(s): @kansi

### Targeted Release
BigchainDB 2.0

## Dependencies
N/A
