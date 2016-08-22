# The Python Driver API by Example

The Python driver API is used by app developers to develop client apps which can communicate with one or more BigchainDB clusters. Under the hood, the Python driver API communicates with the BigchainDB cluster using the BigchainDB HTTP client-server API.

Here's an example of how to use the Python driver API. First, launch an interactive Python session, then:
```python
In [1]: from bigchaindb.client import temp_client
In [2]: c1 = temp_client()
In [3]: c2 = temp_client()
In [4]: tx1 = c1.create()
In [5]: tx1
Out[5]: 
{'assignee': '3NsvDXiiuf2BRPnqfRuBM9yHNjsH4L33gcZ4rh4GMY2J',
 'id': '00f530d210c06671ab2de4330e3e2cf0d0b47b2826302ee25ceea9b2f47b097f',
 'transaction': {'conditions': [{'cid': 0,
    'condition': {'details': {'bitmask': 32,
      'public_key': '9FGRd2jLxmwtRkwsWTpEoqy1rZpg6ycuT7NwmCR4QVk3',
      'signature': None,
      'type': 'fulfillment',
      'type_id': 4},
     'uri': 'cc:4:20:eoUROTxUArrpXGVBrvrYqkcEGG8lB_leliNvSvSddDg:96'},
    'owners_after': ['9FGRd2jLxmwtRkwsWTpEoqy1rZpg6ycuT7NwmCR4QVk3']}],
  'data': {'payload': None, 'uuid': 'b4884e37-3c8e-4cc2-bfc8-68a05ed090ad'},
  'fulfillments': [{'owners_before': ['3NsvDXiiuf2BRPnqfRuBM9yHNjsH4L33gcZ4rh4GMY2J'],
    'fid': 0,
    'fulfillment': 'cf:4:I1IkuhCSf_hGqJ-JKHTQIO1g4apbQuaZXNMEX4isyxd7azkJreyGKyaMLs6Xk9kxQClwz1nQiKM6OMRk7fdusN0373szGbq-PppnsjY6ilbx1JmP-IH7hdjjwjjx9coM',
    'input': None}],
  'operation': 'CREATE',
  'timestamp': '1466676327'},
 'version': 1}

In [6]: c1.transfer(c2.public_key, {'txid': tx1['id'], 'cid': 0})
Out[6]: 
{'assignee': '3NsvDXiiuf2BRPnqfRuBM9yHNjsH4L33gcZ4rh4GMY2J',
 'id': 'd6da7b42c1d82b6a14514bef5c919e7b21e77bc32d537993bc4e5c98d1885e1d',
 'transaction': {'conditions': [{'cid': 0,
    'condition': {'details': {'bitmask': 32,
      'public_key': '89tbMBospYsTNDgpqFS4RLszNsxuE4JEumNuY3WTAnT5',
      'signature': None,
      'type': 'fulfillment',
      'type_id': 4},
     'uri': 'cc:4:20:akjKWxLO2hbe6RVva_FsWNDJmnUKYjQ57HIhUQbwb2Q:96'},
    'owners_after': ['89tbMBospYsTNDgpqFS4RLszNsxuE4JEumNuY3WTAnT5']}],
  'data': {'payload': None, 'uuid': 'a640a9d6-9384-4e9c-a130-e899ea6416aa'},
  'fulfillments': [{'owners_before': ['9FGRd2jLxmwtRkwsWTpEoqy1rZpg6ycuT7NwmCR4QVk3'],
    'fid': 0,
    'fulfillment': 'cf:4:eoUROTxUArrpXGVBrvrYqkcEGG8lB_leliNvSvSddDgVmY6O7YTER04mWjAVd6m0qOv5R44Cxpv_65OtLnNUD-HEgD-9z3ys4GvPf7BZF5dKSbAs_3a8yCQM0bkCcqkB',
    'input': {'cid': 0,
     'txid': '00f530d210c06671ab2de4330e3e2cf0d0b47b2826302ee25ceea9b2f47b097f'}}],
  'operation': 'TRANSFER',
  'timestamp': '1466676463'},
 'version': 1}
```
