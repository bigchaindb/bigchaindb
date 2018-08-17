<!---
Copyright BigchainDB GmbH and BigchainDB contributors
SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
Code is Apache-2.0 and docs are CC-BY-4.0
--->

# How to Store Files in BigchainDB

While it's possible to store a file in a BigchainDB network, we don't recommend doing that. It works best for storing, indexing and querying _structured data_, not files.

If you want decentralized file storage, check out Storj, Sia, Swarm or IPFS/Filecoin. You could store file URLs, hashes or other metadata in a BigchainDB network.

If you really must store a file in a BigchainDB network, then one way to do that is to convert it to a long Base64 string and then to store that string in one or more BigchainDB transactions, either in the `asset.data` of a CREATE transaction, or the `metadata` of any transaction.
