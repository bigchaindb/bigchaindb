
.. Copyright BigchainDB GmbH and BigchainDB contributors
   SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
   Code is Apache-2.0 and docs are CC-BY-4.0

BigchainDB, Privacy and Private Data
------------------------------------

Basic Facts
===========

#. One can store arbitrary data (including encrypted data) in a BigchainDB network, within limits: there’s a maximum transaction size. Every transaction has a ``metadata`` section which can store almost any Unicode string (up to some maximum length). Similarly, every CREATE transaction has an ``asset.data`` section which can store almost any Unicode string.
#. The data stored in certain BigchainDB transaction fields must not be encrypted, e.g. public keys and amounts. BigchainDB doesn’t offer private transactions akin to Zcoin.
#. Once data has been stored in a BigchainDB network, it’s best to assume it can’t be change or deleted.
#. Every node in a BigchainDB network has a full copy of all the stored data.
#. Every node in a BigchainDB network can read all the stored data.
#. Everyone with full access to a BigchainDB node (e.g. the sysadmin of a node) can read all the data stored on that node.
#. Everyone given access to a node via the BigchainDB HTTP API can find and read all the data stored by BigchainDB. The list of people with access might be quite short.
#. If the connection between an external user and a BigchainDB node isn’t encrypted (using HTTPS, for example), then a wiretapper can read all HTTP requests and responses in transit.
#. If someone gets access to plaintext (regardless of where they got it), then they can (in principle) share it with the whole world. One can make it difficult for them to do that, e.g. if it is a lot of data and they only get access inside a secure room where they are searched as they leave the room.

Storing Private Data Off-Chain
==============================

A system could store data off-chain, e.g. in a third-party database, document store, or content management system (CMS) and it could use BigchainDB to:

- Keep track of who has read permissions (or other permissions) in a third-party system. An example of how this could be done is described below.
- Keep a permanent record of all requests made to the third-party system.
- Store hashes of documents-stored-elsewhere, so that a change in any document can be detected.
- Record all handshake-establishing requests and responses between two off-chain parties (e.g. a Diffie-Hellman key exchange), so as to prove that they established an encrypted tunnel (without giving readers access to that tunnel). There are more details about this idea in `the BigchainDB Privacy Protocols repository <https://github.com/bigchaindb/privacy-protocols>`_.

A simple way to record who has read permission on a particular document would be for the third-party system (“DocPile”) to store a CREATE transaction in a BigchainDB network for every document+user pair, to indicate that that user has read permissions for that document. The transaction could be signed by DocPile (or maybe by a document owner, as a variation). The asset data field would contain 1) the unique ID of the user and 2) the unique ID of the document. The one output on the CREATE transaction would only be transferable/spendable by DocPile (or, again, a document owner).

To revoke the read permission, DocPile could create a TRANSFER transaction, to spend the one output on the original CREATE transaction, with a metadata field to say that the user in question no longer has read permission on that document.

This can be carried on indefinitely, i.e. another TRANSFER transaction could be created by DocPile to indicate that the user now has read permissions again.

DocPile can figure out if a given user has read permissions on a given document by reading the last transaction in the CREATE → TRANSFER → TRANSFER → etc. chain for that user+document pair.

There are other ways to accomplish the same thing. The above is just one example.

You might have noticed that the above example didn’t treat the “read permission” as an asset owned (controlled) by a user because if the permission asset is given to (transferred to or created by) the user then it cannot be controlled any further (by DocPile) until the user transfers it back to DocPile. Moreover, the user could transfer the asset to someone else, which might be problematic.

Storing Private Data On-Chain, Encrypted
========================================

There are many ways to store private data on-chain, encrypted. Every use case has its own objectives and constraints, and the best solution depends on the use case. `The BigchainDB consulting team <https://www.bigchaindb.com/services/>`_, along with our partners, can help you design the best solution for your use case.

Below we describe some example system setups, using various crypto primitives, to give a sense of what’s possible.

Please note:

- Ed25519 keypairs are designed for signing and verifying cryptographic signatures, `not for encrypting and decrypting messages <https://crypto.stackexchange.com/questions/27866/why-curve25519-for-encryption-but-ed25519-for-signatures>`_. For encryption, you should use keypairs designed for encryption, such as X25519.
- If someone (or some group) publishes how to decrypt some encrypted data on-chain, then anyone with access to that encrypted data will be able to get the plaintext. The data can’t be deleted.
- Encrypted data can’t be indexed or searched by MongoDB. (It can index and search the ciphertext, but that’s not very useful.) One might use homomorphic encryption to index and search encrypted data, but MongoDB doesn’t have any plans to support that any time soon. If there is indexing or keyword search needed, then some fields of the ``asset.data`` or ``metadata`` objects can be left as plain text and the sensitive information can be stored in an encrypted child-object.

System Example 1
~~~~~~~~~~~~~~~~

Encrypt the data with a symmetric key and store the ciphertext on-chain (in ``metadata`` or ``asset.data``). To communicate the key to a third party, use their public key to encrypt the symmetric key and send them that. They can decrypt the symmetric key with their private key, and then use that symmetric key to decrypt the on-chain ciphertext.

The reason for using a symmetric key along with public/private keypairs is so the ciphertext only has to be stored once.

System Example 2
~~~~~~~~~~~~~~~~

This example uses `proxy re-encryption <https://en.wikipedia.org/wiki/Proxy_re-encryption>`_:

#. MegaCorp encrypts some data using its own public key, then stores that encrypted data (ciphertext 1) in a BigchainDB network.
#. MegaCorp wants to let others read that encrypted data, but without ever sharing their private key and without having to re-encrypt themselves for every new recipient. Instead, they find a “proxy” named Moxie, to provide proxy re-encryption services.
#. Zorban contacts MegaCorp and asks for permission to read the data.
#. MegaCorp asks Zorban for his public key.
#. MegaCorp generates a “re-encryption key” and sends it to their proxy, Moxie.
#. Moxie (the proxy) uses the re-encryption key to encrypt ciphertext 1, creating ciphertext 2.
#. Moxie sends ciphertext 2 to Zorban (or to MegaCorp who forwards it to Zorban).
#. Zorban uses his private key to decrypt ciphertext 2, getting the original un-encrypted data.

Note:

- The proxy only ever sees ciphertext. They never see any un-encrypted data.
- Zorban never got the ability to decrypt ciphertext 1, i.e. the on-chain data.
- There are variations on the above flow.

System Example 3
~~~~~~~~~~~~~~~~

This example uses `erasure coding <https://en.wikipedia.org/wiki/Erasure_code>`_:

#. Erasure-code the data into n pieces.
#. Encrypt each of the n pieces with a different encryption key.
#. Store the n encrypted pieces on-chain, e.g. in n separate transactions.
#. Share each of the the n decryption keys with a different party.

If k < N of the key-holders gets and decrypts k of the pieces, they can reconstruct the original plaintext. Less than k would not be enough.

System Example 4
~~~~~~~~~~~~~~~~

This setup could be used in an enterprise blockchain scenario where a special node should be able to see parts of the data, but the others should not.

- The special node generates an X25519 keypair (or similar asymmetric *encryption* keypair).
- A BigchainDB end user finds out the X25519 public key (encryption key) of the special node.
- The end user creates a valid BigchainDB transaction, with either the asset.data or the metadata (or both) encrypted using the above-mentioned public key.
- This is only done for transactions where the contents of asset.data or metadata don't matter for validation, so all node operators can validate the transaction.
- The special node is able to decrypt the encrypted data, but the other node operators can't, and nor can any other end user.
