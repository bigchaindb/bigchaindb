# Improvement proposals for HTTP API


Currently, there is two milestones grouping issues for upcoming HTTP API
endpoints:

- [Changes that break the existing HTTP API of BDB
  v0.11](https://github.com/bigchaindb/bigchaindb/milestone/11)
- [Changes that are additions to the exiting HTTP API of BDB
  v0.11](https://github.com/bigchaindb/bigchaindb/milestone/9)

After releasing BDB v1.0, breaking changes to the external APIs are not
permitted anymore. Additions to the APIs are however always allowed.

To resolve the outstanding issues, we'll hence limit
the scope of this document to the already existing endpoints.


### First task

Please check the two listed milestones above for the correctness of categorized
issues.


### Methodology

This document will go address each of the issues in the [breaking
changes milestone](https://github.com/bigchaindb/bigchaindb/milestone/11) and
discuss possible solutions to them. Once there is a consensus on the solutions,
we can implement them into BDB core (mainly HTTP API), py and js driver and
the BDB CLI.


### Issues in milestone

#### [Inconsistent naming of short-hand ids](https://github.com/bigchaindb/bigchaindb/issues/1134)

Current naming of ids according to [HTTP API documentation
(master)](https://docs.bigchaindb.com/projects/server/en/master/http-client-server-api.html)
and the [Websocket Event Stream API
(master)](https://docs.bigchaindb.com/projects/server/en/master/websocket-event-stream-api.html):

- Transaction id:
    - `tx_id` in query parameters and Event Stream API
    - `txid` in `transaction.inputs.fulfills`
    - `id` in transaction payload
    - `id` in `/assets?search={text_search}` (this is also the asset's id!)
    - `ID` in prose text
- Asset id:
    - `asset_id` in query parameters and Event Stream API
    - `id` in `transaction.asset` payload
    - `id` in `/assets?search={text_search}` (this is also the transaction's id!)
- Fulfillment id:
    - `type_id` in `transaction.outputs.condition.details`
- Block id:
    - `block_id` in query parameters and Event Stream API
    - `id` in the block payload

General inconsistency: `block_id`, `asset_id` and `tx_id` instead of
`transaction_id`.


Even though, this shouldn't be an argument (as we see the HTTP API descoped
from the underlying implementation):

- [`txid` usage in bdb-server](https://docs.bigchaindb.com/projects/server/en/master/websocket-event-stream-api.html)
- [`txid` usage in bdb-server](https://docs.bigchaindb.com/projects/server/en/master/websocket-event-stream-api.html)


##### Proposal 1

- Call any identifier that points to an object externally is a `object_id`
    - e.g. `transaction.inputs.fulfills.tx_id` points to an external tx, hence
      `_`
- Call any identifier within the data (describing the data) an `id`
    - `transaction.id`, points to itself, hence no need for redundancy in it's
      name

Unfortunately, these rules still leave inconsistencies that are hard to
resolve. Assuming we could agree on `asset_id` and `tx_id` easily, they could
be a nice way forward, as it would mean that we don't have to change a lot of
code:
- `transaction.inputs.fulfills.txid` ==> `transaction.inputs.fulfills.tx_id`
- `id` in /assets?search={text_search} ==> `tx_id` or `asset_id`, as it's the
  /asset endpoint, `asset_id` seems more logical
- In a TRANSFER transaction `transaction.asset.id` would become
`transaction.asset.tx_id` or `transaction.asset.asset_id`

Pros:

- Little changes to code

Contra:

- `asset_id` and `tx_id` need to be resolved for specific cases (mentioned
above) (even though it's not a showstopper)
- Doesn't resolve `tx_id` and `transaction_id` (but can potentially)


##### Proposal 2

- Everything becomes an `id`.

Changes include:

- All query parameters become `id`
- `transaction.outputs.condition.details.type_id` ==>
  `transaction.outputs.condition.details.id` (hard to achieve fix)
- `asset_id`, `tx_id` and `block_id` couldn't be told apart in Websocket Event
  Stream API anymore unless message becomes `{block: {id: "abc"}, asset: {id:
  "def"}, ...}` (which would be OK IMO)

Pros:

- Clean approach
- Easy to apply (also for the future
- Does resolve `tx_id` and `transaction_id`
- `id` is usually clear from context

Contra:

- Lots of changes to be applied to core, drivers, etc.


##### Proposal 3

- Everything becomes `object_id` *or* everything becomes `objectid`

Contra:

- There is huge redundancy in naming e.g. `transaction.tx_id`, etc.
- Lots of changes to be applied
- Doesn't resolve `tx_id` and `transaction_id` (but can potentially)


##### Personal favorite: Proposal 1 then Proposal 2


#### [/outputs?unspents= returns unexpected results](https://github.com/bigchaindb/bigchaindb/issues/1214)

`/outputs?unspent=false` and `/outputs?unspent=true` return same result when no
outputs have been spent on a transaction. [@r-marques's
comment](https://github.com/bigchaindb/bigchaindb/issues/1214#issuecomment-290400956)
does a good job explaining the inconsistency.

Additionally it was brought up that `unspent=true|false` are hard to digest
logic, as there can be double negation:

- `unspent=true`: Return all outputs that have not been spent or "unspent"
- `unspent=false`: Return all outputs that have not been unspent or "spent"
(bit of a stretch to get here in your mind, try it)


##### Proposal 1

- Rename `unspent` to `spent`
* If `spent=true`, response is an array of all spent outputs associated with
  that public key
* If `spent=false`, response is an array of all *NOT YET* spent (or "unspent"
  outputs associated with that public key
* If no unspent= filter, response is an array of all outputs associated with
  that public key (spent and unspent)


Pro:

- Resolves mind-stretch exercise
- Resolves unexpected result when querying the API

Contra:

- Lots of changes to be applied to core, drivers, etc.
- `unspent` is a word of daily communication that we're all used to
`spent=false` not


##### Proposal 2

Based on what @ttmc suggested [here](https://github.com/bigchaindb/bigchaindb/issues/1214#issuecomment-282240980).

* If unspent=true, response is an array of all unspent outputs associated with
  that public key
* If unspent=false, response is an array of all spent outputs associated with
  that public key
* If no unspent= filter, response is an array of all outputs associated with
  that public key (spent and unspent)


Pro:

- Resolves unexpected result when querying the API
- Less changes to be applied to core, drivers, etc. as resolvement 1

Contra:

- Doesn't resolves mind-stretch exercise


##### Proposal 3

Based on what @vrde and @r-marques suggested
[here](https://github.com/bigchaindb/bigchaindb-driver/issues/275) and
[here](https://github.com/bigchaindb/bigchaindb/issues/1214#issuecomment-290400956):

- Rename `unspent` to either `unspent_only` or `exclude_spent` or
`exclude_unspent`.


Pro:

- Expected result = actual result

Contra:

- Doesn't resolve issue properly as the endpoint should:
    - Return an array with both spent and unspent endpoint
    - Return an array with only spent outputs
    - Return an array with only unspent outputs
- Doesn't resolves mind-stretch exercise


##### Personal favorite: Proposal 1


#### [/statuses?tx_id needs to return status invalid](https://github.com/bigchaindb/bigchaindb/issues/1039)

Contra:

- [Is VERY difficult to implement in a consistent manner as we don't store invalid
transactions and since only blocks are marked invalid, transactions are not](https://github.com/bigchaindb/bigchaindb/issues/1039#issuecomment-290424788)
- There is better ways to serve this use case:
    - Tail BDB's logs (generally: provide better debugging capabilities)
    - Listen to the BDB event stream API
    - Event stream API for rejected transactions?

##### Proposal 1

- Generalize use case (e.g. As a BigchainDB user, I want to know when my
  transactions get rejected by a BigchainDB node) and open new ticket
- Close #1039


##### Personal favorite: Proposal 1 lol


#### [/transaction/ID needs status flag](https://github.com/bigchaindb/bigchaindb/issues/1038)

Why? [Because it wasn't implemented according to it's
specification](https://github.com/bigchaindb/bigchaindb/pull/1360/files).

Transactions that have not made it into a valid block yet can be viewed as
uncommited operations in a database. They're not yet persisted and essentially
"do not exist yet" for the database.

##### Proposal 1

- Documentation and implementation are in sync now. Leave everything as is.

Pros:

- No work required

Contra:

- Unsafe method to use for any user that's not specifically aware that
  /transactions/ID returns non-committed (`UNDECIDED`, `BACKLOG`) transactions.
- Ideally, the inner workings of BDB do not need to be fully understood in
  order to work with BDB (compare to databases: Many database users aren't
  experts on the details of the database's inner workings: "What is a BACKLOG,
  and why should I care?")


##### Proposal 2

- /transaction/ID is returning only transactions included in a VALID block


Pros:

- Expected behavior (similar to comparable systems: databases and blockchains
alike)
- Transaction's status can still be monitored at /status, as is expected
- Non-persisted transaction cannot be queried from BDB
- No mental overhead
- Interface is safe: Users will be making mission-critical assumptions on the
  /transactions/id endpoint but might miss the API docs part. We want it's
  default behavior to be as safe as possible
- Querying for UNDECIDED or BACKLOG is very difficult to achieve without
  confusing the user (e.g. [transactions can be in multiple
  states](https://github.com/bigchaindb/bigchaindb/issues/1038#issuecomment-274049790)).
  Safes us and the user lots of time

Contra:

- Transactions from BACKLOG OR UNDECIDED blocks cannot be queried anymore
(actually they can using /blocks and /votes)


##### Proposal 3

- /transaction/ID is returning only transactions included in a VALID block
- /transaction/ID?safe=false (where ?safe=true or lack of is default) may
return transactions from BAcKLOG or UNDECIDED blocks


Pros:

- Expected behavior (similar to comparable systems: databases and blockchains
alike)
- Non-persisted transaction can be queried from BDB (is that a Pro?)
- Interface is safe: Users will be making mission-critical assumptions on the
  /transactions/id endpoint but might miss the API docs part. We want it's
  default behavior to be as safe as possible

Contra:

- Might be used as a substitute endpoint instead of /status?tx_id
- Mental overhead
- Ideally, the inner workings of BDB do not need to be fully understood in
  order to work with BDB (compare to databases: Many database users aren't
  experts on the details of the database's inner workings: "What is a BACKLOG,
  and why should I care?")


#### Proposal 4

- /transactions/id gets a ?status flag

Contra:

- Querying for UNDECIDED or BACKLOG is very difficult to achieve without
  confusing the user (e.g. [transactions can be in multiple
  states](https://github.com/bigchaindb/bigchaindb/issues/1038#issuecomment-274049790))
  Safes us and the user lots of time
- Might be used as a substitute endpoint instead of /status?tx_id
- Ideally, the inner workings of BDB do not need to be fully understood in
  order to work with BDB (compare to databases: Many database users aren't
  experts on the details of the database's inner workings: "What is a BACKLOG,
  and why should I care?")


##### Personal favorite: Proposal 2


#### [/transaction/id and /transaction?asset_id?operation=CREATE return same content](https://github.com/bigchaindb/bigchaindb/issues/1129)

I can't think of any proposal. If anyone has a proposal that makes sense,
please let me know.


#### [Consolidate / and /api/v1](https://github.com/bigchaindb/bigchaindb/issues/1147)


#### Proposal 1

- In `/`, move `/api/v1` inside of `_links`. Remove `docs` destinction.


New endpoint:

```
{
    "_links": {
        "docs": "https://docs.bigchaindb.com/projects/server/en/v0.11.0.dev/http-client-server-api.html",
        "self": "http://example.com:9984/api/v1/",
        "statuses": "http://example.com:9984/api/v1/statuses/",
        "streams_v1": "ws://example.com:9985/api/v1/streams/valid_tx",
        "transactions": "http://example.com:9984/api/v1/transactions/"
    },
    "keyring": [
        "6qHyZew94NMmUTYyHnkZsB8cxJYuRNEiEpXHe1ih9QX3",
    "AdDuyrTyjrDt935YnFu4VBCVDhHtY2Y6rcy7x2TFeiRi"
    ],
    "public_key": "NC8c8rYcAhyKVpx1PCV65CBmyq4YUbLysy3Rqrg8L8mz",
    "software": "BigchainDB",
    "version": "0.11.0.dev"
}
```


##### Proposal X

I tried other proposals, but they all looked weird to me:


```
{
    "_links": {
        "api_v1": {
            "docs": "https://docs.bigchaindb.com/projects/server/en/v0.11.0.dev/http-client-server-api.html",
            "self": "http://example.com:9984/api/v1/",
            "statuses": "http://example.com:9984/api/v1/statuses/",
            "streams_v1": "ws://example.com:9985/api/v1/streams/valid_tx",
            "transactions": "http://example.com:9984/api/v1/transactions/"
        }
        "docs": "https://docs.bigchaindb.com/projects/server/en/v0.11.0.dev/",
    },
    "keyring": [
        "6qHyZew94NMmUTYyHnkZsB8cxJYuRNEiEpXHe1ih9QX3",
    "AdDuyrTyjrDt935YnFu4VBCVDhHtY2Y6rcy7x2TFeiRi"
    ],
    "public_key": "NC8c8rYcAhyKVpx1PCV65CBmyq4YUbLysy3Rqrg8L8mz",
    "software": "BigchainDB",
    "version": "0.11.0.dev"
}
```

In this one, `_links.api_v1`, we forgot another nested `_links`. To fix:

```
{
    "_links": {
        "api_v1": {
            "_links": {
                "docs": "https://docs.bigchaindb.com/projects/server/en/v0.11.0.dev/http-client-server-api.html",
                "self": "http://example.com:9984/api/v1/",
                "statuses": "http://example.com:9984/api/v1/statuses/",
                "streams_v1": "ws://example.com:9985/api/v1/streams/valid_tx",
                "transactions": "http://example.com:9984/api/v1/transactions/"
            }
        }
        "docs": "https://docs.bigchaindb.com/projects/server/en/v0.11.0.dev/",
    },
    "keyring": [
        "6qHyZew94NMmUTYyHnkZsB8cxJYuRNEiEpXHe1ih9QX3",
    "AdDuyrTyjrDt935YnFu4VBCVDhHtY2Y6rcy7x2TFeiRi"
    ],
    "public_key": "NC8c8rYcAhyKVpx1PCV65CBmyq4YUbLysy3Rqrg8L8mz",
    "software": "BigchainDB",
    "version": "0.11.0.dev"
}
```

Now that's weird.


##### Personal favorite: Proposal 1
