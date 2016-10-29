# The Transaction Model

A transaction has the following structure:

```json
{
    "id": "<hash of transaction, excluding signatures (see explanation)>",
    "version": "<version number of the transaction model>",
    "transaction": {
        "fulfillments": ["<list of fulfillments>"],
        "conditions": ["<list of conditions>"],
        "operation": "<string>",
        "timestamp": "<timestamp from client>",
        "asset": "<digital asset description (explained in the next section)>",
        "metadata": {
            "id": "<uuid>",
            "data": "<any JSON document>"
        }
    }
}
```

Here's some explanation of the contents of a transaction:

- `id`: The hash of everything inside the serialized `transaction` body (i.e. `fulfillments`, `conditions`, `operation`, `timestamp` and `data`; see below), with one wrinkle: for each fulfillment in `fulfillments`, `fulfillment` is set to `null`. The `id` is also the database primary key.
- `version`: Version number of the transaction model, so that software can support different transaction models.
- `transaction`:
    - `fulfillments`: List of fulfillments. Each _fulfillment_ contains a pointer to an unspent asset
    and a _crypto fulfillment_ that satisfies a spending condition set on the unspent asset. A _fulfillment_
    is usually a signature proving the ownership of the asset.
    See [Conditions and Fulfillments](#conditions-and-fulfillments) below.
    - `conditions`: List of conditions. Each _condition_ is a _crypto-condition_ that needs to be fulfilled by a transfer transaction in order to transfer ownership to new owners.
    See [Conditions and Fulfillments](#conditions-and-fulfillments) below.
    - `operation`: String representation of the operation being performed (currently either "CREATE", "TRANSFER" or "GENESIS"). It determines how the transaction should be validated.
    - `timestamp`: The Unix time when the transaction was created. It's provided by the client. See [the section on timestamps](timestamps.html).
	- `asset`: Definition of the digital asset. See next section.
    - `metadata`:
        - `id`: UUID version 4 (random) converted to a string of hex digits in standard form.
        - `data`: Can be any JSON document. It may be empty in the case of a transfer transaction.

Later, when we get to the models for the block and the vote, we'll see that both include a signature (from the node which created it). You may wonder why transactions don't have signatures... The answer is that they do! They're just hidden inside the `fulfillment` string of each fulfillment. A creation transaction is signed by the node that created it. A transfer transaction is signed by whoever currently controls or owns it.

What gets signed? For each fulfillment in the transaction, the "fullfillment message" that gets signed includes the `operation`, `timestamp`, `data`, `version`, `id`, corresponding `condition`, and the fulfillment itself, except with its fulfillment string set to `null`. The computed signature goes into creating the `fulfillment` string of the fulfillment.

One other note: Currently, transactions contain only the public keys of asset-owners (i.e. who own an asset or who owned an asset in the past), inside the conditions and fulfillments. A transaction does _not_ contain the public key of the client (computer) which generated and sent it to a BigchainDB node. In fact, there's no need for a client to _have_ a public/private keypair. In the future, each client may also have a keypair, and it may have to sign each sent transaction (using its private key); see [Issue #347 on GitHub](https://github.com/bigchaindb/bigchaindb/issues/347). In practice, a person might think of their keypair as being both their "ownership-keypair" and their "client-keypair," but there is a difference, just like there's a difference between Joe and Joe's computer.