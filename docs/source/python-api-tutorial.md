# Getting started with the HTTP API

The preferred way to communicate with a Node in the BigchainDB Federation is via HTTP requests.
Each Node exposes a simple HTTP API that provides, right now, two endpoints, one to get information about a specific
transaction id, one to push transactions to the BigchainDB network.

The endpoints are documented in [Apiary](http://docs.bigchaindb.apiary.io/).


## Usage example using the Python client

```python
In [1]: from bigchaindb.client import temp_client
In [2]: c1 = temp_client()
In [3]: c2 = temp_client()
In [4]: tx1 = c1.create()
In [5]: tx1
Out[5]:
{'assignee': '2Bi5NUv1UL7h3ZGs5AsE6Gr3oPQhE2vGsYCapNYrAU4pr',
'id': '26f21d8b5f9731cef631733b8cd1da05f87aa59eb2f939277a2fefeb774ae133',
'signature': '304402201b904f22e9f5a502070244b64822adf28...',
'transaction': {'current_owner': '2Bi5NUv1UL7h3ZGs5AsE6Gr3oPQhE2vGsYCapNYrAU4pr',
 'data': {'hash': 'efbde2c3aee204a69b7696d4b10ff31137fe78e3946306284f806e2dfc68b805',
  'payload': None},
 'input': None,
 'new_owner': '247epGEcoX9m6yvR6sEZvYGb1XCpUUWtCNUVKgJGrFWCr',
 'operation': 'CREATE',
 'timestamp': '1456763521.824126'}}
In [7]: c1.transfer(c2.public_key, tx1['id'])
Out[7]:
{'assignee': '2Bi5NUv1UL7h3ZGs5AsE6Gr3oPQhE2vGsYCapNYrAU4pr',
'id': '34b62c9fdfd93f5907f35e2495239ae1cb62e9519ff64a8710f3f77a9f040857',
'signature': '3046022100b2b2432c20310dfcda6a2bab3c893b0cd17e70fe...',
'transaction': {'current_owner': '247epGEcoX9m6yvR6sEZvYGb1XCpUUWtCNUVKgJGrFWCr',
 'data': {'hash': 'efbde2c3aee204a69b7696d4b10ff31137fe78e3946306284f806e2dfc68b805',
  'payload': None},
 'input': '26f21d8b5f9731cef631733b8cd1da05f87aa59eb2f939277a2fefeb774ae133',
 'new_owner': 'p5Ci1KJkPHvRBnxqyq36m8GXwkWSuhMiZSg8aB1ZrZgJ',
 'operation': 'TRANSFER',
 'timestamp': '1456763549.446138'}}
```


# Roadmap

The development of the API is still at the beginning and you can follow it on
[GitHub](https://github.com/bigchaindb/bigchaindb/issues?q=is%3Aissue+is%3Aopen+label%3Arest-api)

There are several key features still missing like:
 - validating the structure of the transaction
 - returns the correct error codes if something goes wrong
 - add an endpoint to query unspents for a given public key

