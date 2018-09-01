
.. Copyright BigchainDB GmbH and BigchainDB contributors
   SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
   Code is Apache-2.0 and docs are CC-BY-4.0

BigchainDB and Smart Contracts
==============================

One can store the source code of any smart contract (i.e. a computer program) in BigchainDB, but BigchainDB won't run arbitrary smart contracts.

BigchainDB can be used to enforce who has permission to transfer assets, both fungible assets and non-fungible assets. It will prevent double-spending. In other words, a BigchainDB network could be used instead of an ERC-20 (fungible token) or ERC-721 (non-fungible token) smart contract.

Asset transfer permissions can also be interpreted as write permissions, so they can be used to control who can write to a log, journal or audit trail. There is more about that idea in :ref:`the page about permissions in BigchainDB <permissions-in-bigchaindb>`.

A BigchainDB network can be connected to other blockchain networks, via oracles or inter-chain communications protocols. That means BigchainDB can be used as part of a solution that uses *other* blockchains to run arbitrary smart contracts.
