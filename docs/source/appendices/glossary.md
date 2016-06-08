# Glossary of Terms

**BigchaindB client.** A computer that can communicate with a BigchainDB cluster via the BigchainDB client-server API.

**BigchainDB cluster.** A collection of servers running BigchainDB Server software and communicating with each other via RethinkDB protocols. a BigchainDB cluster contains one logical RethinkDB datastore.

**Block.** A collection of up to 1000 transactions, plus other things. They get chained together by votes. See [the section on the block model](../topic-guides/models.html#the-block-model).

**Federation.** 1. An organization with members and some kind of governance structure. 2. The BigchainDB cluster owned and operated by a Federation's members.

**Federation node.** A server running BigchainDB Server software, with permission to communicate with other nodes in a federation.

**Node.** See _Federation node_.

**Transaction.** The basic informational unit. A transaction can represent the creation or transfer of a digital asset. See [the section on the transaction model](../topic-guides/models.html#the-transaction-model).

**Vote.** Each federation node in a federation is required to vote on the validity of every block (i.e. whether the block valid or not). A node's vote on a block also includes the id of the block it considers to be the previous block. See [the section on the vote model](../topic-guides/models.html#the-vote-model).
