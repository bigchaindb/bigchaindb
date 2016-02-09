# Frequently Asked Questions (FAQ)

## Questions About the BigchainDB Whitepaper

**Question 1?**

Answer 1.

**Question 2?**

Answer 2.

## Other Questions

**Why do we use blocks and not just create the chain with transactions?**

With distributed data stores there is no guarantees in the order in which transactions will be commited to the database. Witouth knowing what is previous transactions to be commited to the database we cannot include its hash in the current transaction to build the chain.

To solve this problem we decided to use blocks and create the chain with the blocks.
