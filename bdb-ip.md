# Improvement proposals for HTTP API


Currently, there is two milestones grouping issues for upcoming HTTP API
endpoints:

- [Changes that break the existing HTTP API of BDB
  v0.11](https://github.com/bigchaindb/bigchaindb/milestone/11)
- [Changes that are additions to the exiting HTTP API of BDB
  v0.11](https://github.com/bigchaindb/bigchaindb/milestone/9)

After releasing BDB v1.0, breaking changes to the external APIs that are not:

- show stopper-bug fixes; or
- security considerations

won't be permitted anymore. Additions to the APIs are however always allowed.

To resolve the outstanding issues, we'll hence limit the scope of this document
to the already existing endpoints.


## First task

Please check the two listed milestones above for the correctness of categorized
issues.


## Methodology

This document will go address each of the issues in the [breaking
changes milestone](https://github.com/bigchaindb/bigchaindb/milestone/11) and
discuss possible solutions to them. Once there is a consensus on the solutions,
we can implement them into BDB core (mainly HTTP API), py and js driver and
the BDB CLI.

All issues are ordered in a dependency graph to avoid backtracking in decision
making and merge conflicts in implementation (root nodes do not have
dependencies):

- 0. What does "breaking change" mean
    - 1. Inconsistent naming of short-hand ids
    - 2. Inconsistency in using relative links
        - 3. Consolidate / and /api/v1
            - 4. Remove host and port from URLs in API and root endpoint
        - 5. /outputs?unspents= returns unexpected results
            - 6. A new /outputs endpoint
- 7. /statuses?tx_id needs to return status invalid
- 8. /transaction/ID needs status flag
- 9. /transaction/id and /transaction?asset_id?operation=CREATE return same content
- 10. Include block_id and transaction status in /transactions/id


## Second task

Please make sure the proposed dependency graph is correct.


## Issues in milestone

In this section, we'll go over each of the changes ordered by the above
dependency tree.


### [0. What does "breaking change" mean?](https://github.com/bigchaindb/bigchaindb/pull/1522#discussion_r120822313)

@krish7919 wrote:

```
Suppose we change something in BigchainDB API, and make the corresponding
changes to the (officially) supported drivers, can we claim that as long as the
driver API (with the user programs) remain the same, the change is permissible.
That might give us more leeway going forward if we come up with something
unexpected.
```


#### Proposal 1

Breaking changes means, every change provoking an incompatibility for the
following components:

- HTTP API
- Events API
- official Python driver
- official Javascript driver


#### Proposal 2

Breaking changes means, every change provoking an incompatibility for the
following components:

- official Python driver
- official Javascript driver

Notice that compatibility is achieved here through officially supported
drivers that update according to the breaking changes in the HTTP and Events
API.


#### Favorite Proposal: Proposal 1

Proposal 1, as we only have two official driver and several users are in the
process of building drivers.


### [1. Inconsistent naming of short-hand ids](https://github.com/bigchaindb/bigchaindb/issues/1134)

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
- Block id:
    - `block_id` in query parameters and Event Stream API
    - `id` in the block payload

General inconsistency: `block_id`, `asset_id` and `tx_id` instead of
`transaction_id`.

[As pointed out by
@r-marques](https://github.com/bigchaindb/bigchaindb/pull/1522#discussion_r120815083),
we'll ignore `type_id` in a Crypto-condition fulfillment for the scope of this
discussion.


Even though, this shouldn't be an argument (as we see the HTTP API descoped
from the underlying implementation):

- [`txid` usage in bdb-server](https://github.com/bigchaindb/bigchaindb/search?utf8=%E2%9C%93&q=txid&type=)
- [`tx_id` usage in bdb-server](https://github.com/bigchaindb/bigchaindb/search?utf8=%E2%9C%93&q=tx_id&type=)


#### Proposal 1

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


#### Proposal 2

- Everything becomes an `id`.

Changes include:

- All query parameters become `id`
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


#### Proposal 3

- Everything becomes `object_id` *or* everything becomes `objectid`

Contra:

- There is huge redundancy in naming e.g. `transaction.tx_id`, etc.
- Lots of changes to be applied
- Doesn't resolve `tx_id` and `transaction_id` (but can potentially)


#### Personal favorite: Proposal 1 then Proposal 2


### [2. Inconsistency in using relative links](https://github.com/bigchaindb/bigchaindb/issues/1525)

See [/outputs endpoint](https://docs.bigchaindb.com/projects/server/en/master/http-client-server-api.html#get--api-v1-outputs?public_key=public_key)


``` [
"../transactions/2d431073e1477f3073a4693ac7ff9be5634751de1b8abaa1f4e19548ef0b4b0e/outputs/0",
"../transactions/2d431073e1477f3073a4693ac7ff9be5634751de1b8abaa1f4e19548ef0b4b0e/outputs/1"
]
```

where the output endpoint's result also contains the output's index.
The [/status endpoint](https://docs.bigchaindb.com/projects/server/en/master/http-client-server-api.html#get--api-v1-statuses?tx_id=tx_id)

```
{
    "status": "valid",
    "_links": { "tx":
        "/transactions/38100137cea87fb9bd751e2372abb2c73e7d5bcf39d940a5516a324d9c7fb88d"
    }
}
```

notice `_links` being used here (both blocks and transactions).
This pattern is not repeated in `/assets`, the events API, `/blocks?tx_id`


#### Proposal 1

- Remove all relative links and usage of `_links` when linking to specific
  resources (doesn't count for `_links` in `/` and `/api/v1` endpoint.
- In `/status`, rename `tx` to whatever the outcome of issue 1. is. Remove
  `_links`.
- In `/status`, rename `block` to whatever the outcome of issue 1. is
- In `/outputs` instead of relatively linking to `../transactions/...`, return
  list of objects like (syntax not for debate here, see issue 8.): `{"tx_id":
  "abc", "output": 0, ...}`


#### Proposal 2

- Remove *ALL* `_links` and just point (links would still stay, but extra
  nesting via `_links` would be removed)
- In `/status`, rename `tx` to whatever the outcome of issue 1. is. Remove
  `_links`.
- In `/status`, rename `block` to whatever the outcome of issue 1. is
- In `/outputs` instead of relatively linking to `../transactions/...`, return
  list of objects like (syntax not for debate here, see issue 8.): `{"tx_id":
  "abc", "output": 0, ...}`

An example for `/` (assuming we don't do anything with issue 6.):

```
{
    "api_v1": "http://example.com:9984/api/v1/",
    "docs": "https://docs.bigchaindb.com/projects/server/en/v0.11.0.dev/"
    "keyring": [
        "6qHyZew94NMmUTYyHnkZsB8cxJYuRNEiEpXHe1ih9QX3",
        "AdDuyrTyjrDt935YnFu4VBCVDhHtY2Y6rcy7x2TFeiRi"
    ],
    "public_key": "NC8c8rYcAhyKVpx1PCV65CBmyq4YUbLysy3Rqrg8L8mz",
    "software": "BigchainDB",
    "version": "0.11.0.dev"
}
```

An example for `/api/v1` (assuming we don't do anything with issue 6.):


```
{
    "docs": "https://docs.bigchaindb.com/projects/server/en/v0.11.0.dev/http-client-server-api.html",
    "self": "http://example.com:9984/api/v1/",
    "statuses": "http://example.com:9984/api/v1/statuses/",
    "streams_v1": "ws://example.com:9985/api/v1/streams/valid_tx",
    "transactions": "http://example.com:9984/api/v1/transactions/"
}
```

You get the idea.


Pro:

- We don't know of any dynamic clients at this point
- JSON-LD is addressing this problem in a nicer way


Contra:

- More work (but not really)
- Influences issue 6.


#### Proposal 3

Implement [HATEOAS](https://en.wikipedia.org/wiki/HATEOAS) properly for
HATEOAS clients to consume the API.


Pro:

- enables dynamic clients


Contra:

- HATEOAS is old and not commonly used; seems like a dying idea, especially
  with JSON-LD on the rise


#### Favorite proposal: Proposal 2


### [3. Consolidate / and /api/v1](https://github.com/bigchaindb/bigchaindb/issues/1147)


#### Proposal 1

- In `/`, move `/api/v1` inside of `_links`. Remove `docs` destinction.
- `/api/v1` must 301 Redirect to `/` (to not break existing deployments)


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


#### Proposal 2

- Don't change.

@ttmc:

```
I think there is a meaningful semantic difference between a server (at /) and
an API (at /api/v1), and therefore I don't favour deleting one of those
endpoints.

The [Kubernetes deployment of BigchainDB
Server](https://github.com/bigchaindb/bigchaindb/blob/master/k8s/bigchaindb/bigchaindb-dep.yaml)
currently uses the `GET /` endpoint for its livenessProbe and readinessProbe,
although [there is a proposal to create a health
endpoint](https://github.com/bigchaindb/bigchaindb/issues/1253) for that
instead.
```


#### Proposal X

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


#### Personal favorite: Proposal 1


### [4. Remove host and port from URLs in API and root endpoint](https://github.com/bigchaindb/bigchaindb/issues/1141)


Root and API endpoint contains redundant information (host and port).
An example:

```
curl -X GET http://localhost:59984/
{
  "_links": {
      "api_v1": "http://localhost:59984/api/v1/", <------ *redundancy*
      ...
  },...
}
```


#### Proposal 1

- Make host and port freely configurable via BigchainDB config file
    - Possibilities include: `""`, but also `"."` for relative URLs
    - `"."` is default option provided in configuration

Pros:

- Removes redundancy in links
- allows for any configuration or approach
- allows for later implementation as not necessary breaking

Contra:

- Allows for incorrect configurations


#### Proposal 2

- Remove host and port from links in `/` and `/api/v1`. Make links relative.

```
curl -X GET http://localhost:59984/
{
  "_links": {
      "api_v1": "./api/v1/",
  },...
}
```

Pros:

- Removes redundancy in links
- Unlikely to have incorrect configurations or setups

Contra:

- No configuration possible still (but then again: nobody ever asked for that?)


#### Personal favorite: Proposal 1


### [5. /outputs?unspents= returns unexpected results](https://github.com/bigchaindb/bigchaindb/issues/1214)

`/outputs?unspent=false` and `/outputs?unspent=true` return same result when no
outputs have been spent on a transaction. [@r-marques's
comment](https://github.com/bigchaindb/bigchaindb/issues/1214#issuecomment-290400956)
does a good job explaining the inconsistency.

Additionally it was brought up that `unspent=true|false` are hard to digest
logic, as there can be double negation:

- `unspent=true`: Return all outputs that have not been spent or "unspent"
- `unspent=false`: Return all outputs that have not been unspent or "spent"
(bit of a stretch to get here in your mind, try it)


#### Proposal 1

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


#### Proposal 2

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


#### Proposal 3

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


#### Personal favorite: Proposal 1


### 6. A new /outputs endpoint

It was put forth many times that the /outputs endpoint is currently flawed due
to it's query limitations. A few examples include:

- [/outputs returns only ed25519 public keys](https://github.com/bigchaindb/bigchaindb/issues/1523)
- [/outputs endpoint needs more information](https://github.com/bigchaindb/bigchaindb/issues/1227)
- etc.

In this attempted, we're going to collect all use cases to redesign the
endpoint from the ground up.

#### Use case 1: Ed25519 outputs

As a BigchainDB user
I want to retrieve all Ed25519 outputs from multiple transactions for given public keys
so that I can create a follow-up TRANSFER transaction.


##### Scenario 1.1: Query for single either spent or unspent Ed25519 output

Given a valid transaction with a single either spent or unspent Ed25519 output exists
When a BigchainDB user is querying BigchainDB for an either spent or unspent output with a specific public key
Then BigchainDB returns all required fractals of information to generate a follow-up TRANSFER transaction for the existing either spent or unspent output.


##### Scenario 1.2: Query for multiple either spent or unspent Ed25519 outputs with single distinct public key

Given a valid transaction with multiple unspent Ed25519 outputs exists
When a BigchainDB user is querying BigchainDB for an unspent output with a specific public key
Then BigchainDB returns all required fractals of information to generate a follow-up TRANSFER transaction for the existing either spent or unspent output.


##### Scenario 1.3: Query for multiple either spent or unspent Ed25519 outputs with multiple distinct public keys

Given a valid transaction with multiple either spent or unspent Ed25519 outputs exists
When a BigchainDB user is querying BigchainDB for either spent or unspent outputs with specific public keys
Then BigchainDB returns all required fractals of information to generate a follow-up TRANSFER transaction for the existing either spent or unspent outputs.


##### Scenario 1.4: Query for multiple either spent or unspent Ed25519 outputs with single distinct public keys

Given a valid transaction with multiple either spent or unspent Ed25519 outputs exists
When a BigchainDB user is querying BigchainDB for either spent or unspent outputs with a specific public key
Then BigchainDB returns all required fractals of information to generate a follow-up TRANSFER transaction for the existing unspent output.


##### Scenario 1.5: Query for multiple either spent or unspent Ed25519 outputs with multiple keys where some outputs are missing

Given one or more valid existing transactions with either spent or unspent Ed25519 outputs
When a BigchainDB user is querying BigchainDB for either spent or unspent outputs with specific public keys
And some specific public keys do not match any existing either spent or unspent outputs in BigchainDB
Then BigchainDB returns for all either spent or unspent outputs matching specific public keys all required fractals of information to generate a follow-up TRANSFER transaction
And the BigchainDB user is not notified about potentially unmatched either spent or unspent outputs.


#### Use case 2: Sha256Threshold outputs

As a BigchainDB user
I want to retrieve all Sha256Threshold outputs from multiple transactions for given public keys
so that I can create a follow-up TRANSFER transaction.


##### Scenario 2.1: Query for single Sha256Threshold output with single public key

Given a valid transaction with a single spent or unspent Sha256Threshold output composed from one or more Ed25519 outputs exists
When a BigchainDB user is querying BigchainDB for a spent or unspent output with a specific public key
Then BigchainDB returns all required fractals of information to generate a follow-up TRANSFER transaction for the existing either spent or unspent output.


##### Scenario 2.2: Query for single Sha256Threshold output with multiple keys

Given a valid transaction with a single spent or unspent Sha256Threshold output composed from one or more Ed25519 outputs exists
When a BigchainDB user is querying BigchainDB for a spent or unspent output with specific public keys
Then BigchainDB returns all fractal information to generate a follow-up TRANSFER transaction matching at least parts of the specific public keys.

For clarification: exxisting output `Sha256Threshold from ["abc", "bcd",
"cde"]`, would match with any of the following combinations (syntax randomly
picked):

- `?public_key=abc&public_key=bcd`
- `?public_key=abc`
- `?public_key=abc&public_key=cde`
- `?public_key=abc&public_key=bcd&public_key=cde`
- as well as all similar combinations.

It wouldn't match however:

- `public_key=def`
- `public_key=abc&public_key=def`
- as well as all similar combinations.


Note: This syntax implies using:

- `&` as a logical AND operator
- `|` as a logical OR operator.

At this point, it's not clear if this is functionality we actually need to
provide.


##### Scenario 2.3: Query for multiple either spent or unspent Sha256Threshold outputs with multiple keys

Given a valid transaction with a multiple either spent or unspent Sha256Threshold outputs composed from one or more Ed25519 outputs exists
When a BigchainDB user is querying BigchainDB for spent or unspent outputs with specific public keys
Then BigchainDB returns all required fractals of information to generate a follow-up TRANSFER transaction for the existing matching outputs.

Note: See clarification in Scenario 2.


##### Scenario 2.4: Query for multiple either spent or unspent Sha256Threshold outputs with multiple keys where some outputs are missing

Given one or more valid existing transactions with either spent or unspent Threshold outputs
When a BigchainDB user is querying BigchainDB for either spent or unspent outputs with specific public keys
And some specific public keys do not match any existing either spent or unspent outputs in BigchainDB
Then BigchainDB returns for all either spent or unspent outputs matching specific public keys all required fractals of information to generate a follow-up TRANSFER transaction
And the BigchainDB user is not notified about potentially not matched either spent or unspent outputs.

Note: See clarification in Scenario 2.


#### Use case 3: Sha256Threshold and Ed25519 outputs mixed

As a BigchainDB user
I want to retrieve all Sha256Threshold outputs and/or Ed25519 outputs from multiple transactions for given public keys
so that I can create a follow-up TRANSFER transaction.


##### Scenario 3.1: Query for single or multiple non-existing Ed25519 or Sha256Treshold output(s) with single or multiple public keys

Given non-existent transactions
When a BigchainDB user is querying BigchainDB for spent or unspent outputs with a single or multiple public keys
And no output in any transactions in BigchainDB matches the given public key(s)
Then a BigchainDB user is notified that no outputs for given public key(s) exist.


##### Scenario 3.2: Query for single or multiple either spent or unspent Ed25519 or Sha256Threshold outputs with single or multiple keys

Given a valid transaction with single or multiple either spent or unspent Sha256Threshold outputs composed from one or more Ed25519 outputs or single or multiple either spent or unspent Ed25519 outputs exists
When a BigchainDB user is querying BigchainDB for spent or unspent output(s) with specific public key(s)
Then BigchainDB returns all required fractals of information to generate a follow-up TRANSFER transaction for the existing matching output(s).


#### Use case 4: Result atomicity and verifiability

There is two competing arguments:

- [/outputs should return atomic and verifiable objects](https://github.com/bigchaindb/bigchaindb/issues/835)
- [/outputs should return 'usable', optional verifiable objects](https://github.com/bigchaindb/bigchaindb/issues/1227)

A potential solution could introduce an `safe=true|false` query parameter
(where default `safe=true` to include a list of outputs into the result (that
are potentially unsafe to use as a node could lie to a user). Querying a
transaction from 2/3 of the network and comparing hashes is the only safe
option currently.


#### Use case 5: (Un)Spendable flag for specific public key

As a BigchainDB user
I want to retrieve outputs based on public keys I flag as either spent or unspent.

@TimDaub: "It's not clear if this is a confirmed use case."


#### Use case 6: [Outputs filtered by specific asset(s)](https://github.com/bigchaindb/bigchaindb/issues/1473)

- Add `?asset_id` to query parameters and filter by


#### Proposed /outputs endpoint design


##### /outputs path definition

In summary, this leaves us with the following possible expression for querying
the new /outputs endpoint:

```
/outputs?public_key={public_key}[&[public_key={public_key}|asset_id={asset_id}]]*&spent=[true|false]&safe=[true|false]
```

Notes:

- `public_key` and `asset_id` are repeatable arbitrarily.
- `spent` is assuming a prior issue had favored a certain proposal


##### /outputs return definition


1. `safe=true` or a lack of returns the following data structure:

```
[{
    "tx_id": "abc",
    "output": 0,
    "asset_id: "e.g. abc - depending on what transaction operation",
    "amount": 1 // for divisible assets
}, ...]
```

Notes:
- We include `asset_id` and `amount` to allow for easier decision making
which transactions to download
- We do **not** include the full output, as for security reasons we want the
user to download the full transaction payload from 2/3 of the network


2. `safe=false` returns the following data structure:

```
[{
    "tx_id": "abc",
    "output": {
        "amount": 1,
        "condition": {
            "details": {
                "bitmask": 32,
                "public_key": "4K9sWUMFwTgaDGPfdynrbxWqWS6sWmKbZoTjxLtVUibD",
                "signature": null,
                "type": "fulfillment",
                "type_id": 4
            },
            "uri": "cc:4:20:MTmLrdyfhfxPw3WxnaYaQkPmU1GcEzg9mAj_O_Nuv5w:96"
        },
        "public_keys": [
            "4K9sWUMFwTgaDGPfdynrbxWqWS6sWmKbZoTjxLtVUibD"
        ]
    },
    "asset_id": "e.g. abc - depending on what transaction operation",
},
{
    "tx_id": "abc",
    "output": {
        "amount": 1,
        "condition": {
            "details": {
                "bitmask": 32,
                "public_key": "def",
                "signature": null,
                "type": "fulfillment",
                "type_id": 4
            },
            "uri": "cc:4:20:MTmLrdyfhfxPw3WxnaYaQkPmU1GcEzg9mAj_O_Nuv5w:96"
        },
        "public_keys": [
            "def"
        ]
    },
    "asset_id": "e.g. abc - depending on what transaction operation",
}]
```

Notes:

- No matter whether or not a returned transaction is of type CREATE or
  TRANSFER, an `asset_id` **is** returned.
- `asset_id` and `tx_id` in case of a CREATE transaction is equal
- Has a transaction two outputs that match the given path, then these are
returned separately in two objects (see that second output's public key doesn't
match first ones, but both have same `tx_id`)
- Note that `amount` is included in `output`


### [7. /statuses?tx_id needs to return status invalid](https://github.com/bigchaindb/bigchaindb/issues/1039)

Contra:

- [Is VERY difficult to implement in a consistent manner as we don't store invalid
transactions and since only blocks are marked invalid, transactions are not](https://github.com/bigchaindb/bigchaindb/issues/1039#issuecomment-290424788)
- There is better ways to serve this use case:
    - Tail BDB's logs (generally: provide better debugging capabilities)
    - Listen to the BDB event stream API
    - Event stream API for rejected transactions?

#### Proposal 1

- Generalize use case (e.g. As a BigchainDB user, I want to know when my
  transactions get rejected by a BigchainDB node) and open new ticket
- Close #1039


#### Personal favorite: Proposal 1 lol


### [8. /transaction/ID needs status flag](https://github.com/bigchaindb/bigchaindb/issues/1038)

Why? [Because it wasn't implemented according to it's
specification](https://github.com/bigchaindb/bigchaindb/pull/1360/files).

Transactions that have not made it into a valid block yet can be viewed as
uncommited operations in a database. They're not yet persisted and essentially
"do not exist yet" for the database.

#### Proposal 1

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


#### Proposal 2

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


#### Proposal 3

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


#### Personal favorite: Proposal 2


### [9. /transaction/id and /transaction?asset_id?operation=CREATE return same content](https://github.com/bigchaindb/bigchaindb/issues/1129)

I can't think of any proposal. If anyone has a proposal that makes sense,
please let me know.


### [10. Include block_id and transaction status in /transactions/id](https://github.com/bigchaindb/bigchaindb/issues/1169)


#### Proposal 1

- Don't do anything.


Why: [read
this](https://blog.codinghorror.com/the-rise-and-fall-of-homo-logicus/) ([and
this](https://www.amazon.com/exec/obidos/ASIN/0672316498/codihorr-20))

TL:DR

```
Homo logicus are driven by an irresistible desire to understand how things
work. By contrast, Homo sapiens have a strong desire for success.

[...]
Pity the poor user, merely a Homo Sapiens, who isn't interested in computers
[or blockchains] or complexity; they just want to get their job done.
```

Notice the functionality described is [anyways included in the HTTP API
already.](https://docs.bigchaindb.com/projects/server/en/latest/http-client-server-api.html#get--api-v1-blocks?tx_id=tx_id&status=UNDECIDED|VALID|INVALID)

#### Favorite Proposal: Proposal 1
