# Transaction Concepts

In BigchainDB, _Transactions_ are used to register, issue, create or transfer
things (e.g. assets).

Transactions are the most basic kind of record stored by BigchainDB. There are
two kinds: CREATE transactions and TRANSFER transactions.

## CREATE Transactions

A CREATE transaction can be used to register, issue, create or otherwise
initiate the history of a single thing (or asset) in BigchainDB. For example,
one might register an identity or a creative work. The things are often called
"assets" but they might not be literal assets.

BigchainDB supports divisible assets as of BigchainDB Server v0.8.0.
That means you can create/register an asset with an initial quantity,
e.g. 700 oak trees. Divisible assets can be split apart or recombined
by transfer transactions (described more below).

A CREATE transaction also establishes, in its outputs, the conditions that must
be met to transfer the asset(s). The conditions may also be associated with a
list of public keys that, depending on the condition, may have full or partial
control over the asset(s). For example, there may be a condition that any
transfer must be signed (cryptographically) by the private key associated with a
given public key. More sophisticated conditions are possible. BigchainDB's
conditions are based on the crypto-conditions of the [Interledger Protocol
(ILP)](https://interledger.org/).

## TRANSFER Transactions

A TRANSFER transaction can transfer an asset
by providing inputs which fulfill the current output conditions on the asset.
It must also specify new transfer conditions.

**Example 1:** Suppose a red car is owned and controlled by Joe.
Suppose the current transfer condition on the car says
that any valid transfer must be signed by Joe.
Joe and a buyer named Rae could build a TRANSFER transaction containing
an input with Joe's signature (to fulfill the current output condition)
plus a new output condition saying that any valid transfer
must be signed by Rae.

**Example 2:** Someone might construct a TRANSFER transaction
that fulfills the output conditions on four
previously-untransferred assets of the same asset type
e.g. paperclips. The amounts might be 20, 10, 45 and 25, say,
for a total of 100 paperclips.
The TRANSFER transaction would also set up new transfer conditions.
For example, maybe a set of 60 paperclips can only be transferred
if Gertrude signs, and a separate set of 40 paperclips can only be
transferred if both Jack and Kelly sign.
Note how the sum of the incoming paperclips must equal the sum
of the outgoing paperclips (100).

## Transaction Validity

When a node is asked to check if a transaction is valid, it checks several
things. We documented those things in a post on the BigchainDB Blog.

TODO (Troy): Hyperlink to the actual post, once it's published.
