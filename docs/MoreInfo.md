
## Full Decentralization and Byzantine Fault Tolerance

BigchainDB leverages Tendermint for networking and consensus, providing:

- Byzantine Fault Tolerance (BFT): The system is highly resilient because Tendermint, the technology behind it, ensures BFT. Even if some nodes misbehave or fail, the network remains secure.
- Local Databases: Each node has its own local MongoDB database. This setup enhances security. If one database is compromised, only that node is affected; others remain unharmed.
- Changing Block Proposers: The system design periodically changes the node responsible for proposing blocks, making it more secure and less predictable.
- True Decentralization: In an ideal BigchainDB 2.0 network, each node is owned and operated by a different entity. This results in full decentralization, with no single owner, controller, or point of failure.
- Global Node Distribution: Nodes should be located in various countries and hosting providers to ensure network robustness. Even if some nodes fail or face issues, the network continues to function.
- High Fault Tolerance: Up to one-third of the nodes can fail or misbehave, and the network will still operate smoothly. The remaining nodes collaborate to make decisions and keep the system running.

## Immutability 

BigchainDB ensures data immutability using several strategies: 

- No Data Alteration APIs: BigchainDB doesn't provide tools to change or erase stored data, making it resistant to unauthorized modifications. 
- Local Copies on Every Node: Each node has its own complete copy of the data in separate MongoDB databases. Even if one node fails, others still have the data, preventing data loss. 
- Cryptographic Signatures: Every transaction is cryptographically signed. If someone tries to change a transaction, the signature changes, which can be detected. Even changing the public key is noticeable since all transactions are signed by known nodes.

## Owner-Controlled Assets 

BigchainDB operates like many other blockchains, where assets are controlled by their owners. 

- User-Defined Assets: BigchainDB allows users to create their own assets as needed, each cryptographically signed by its creator. 

## High Transaction Rate 

BigchainDB is designed to handle a high number of transactions per second, even in challenging conditions. 

## Sybil Tolerance 

In a BigchainDB network, the organization governing the network controls the member list, eliminating the possibility of Sybil attacks.

## Identity Management 

BigchainDB combines the best of blockchains and databases to provide a secure and scalable solution for managing identities.

## BigchainDB Transactions

Creating a BigchainDB transaction is like filling out a form with clear instructions. BigchainDB drivers ensure you follow those instructions to create a valid transaction.