# JSON Serialization

We needed to clearly define how to serialize a JSON object to calculate the hash.

The serialization should produce the same byte output independently of the architecture running the software. If there are differences in the serialization, hash validations will fail although the transaction is correct.

For example, consider the following two methods of serializing `{'a': 1}`:
```python
# Use a serializer provided by RethinkDB
a = r.expr({'a': 1}).to_json().run(b.connection)
u'{"a":1}'

# Use the serializer in Python's json module
b = json.dumps({'a': 1})
'{"a": 1}'

a == b
False
```

The results are not the same. We want a serialization and deserialization so that the following is always true:
```python
deserialize(serialize(data)) == data
True
```

Since BigchainDB performs a lot of serialization we decided to use [python-rapidjson](https://github.com/python-rapidjson/python-rapidjson)
which is a python wrapper for [rapidjson](https://github.com/miloyip/rapidjson) a fast and fully RFC complient JSON parser.

```python
import rapidjson

rapidjson.dumps(data, skipkeys=False,
                ensure_ascii=False,
                sort_keys=True)
```

- `skipkeys`: With skipkeys `False` if the provided keys are not a string the serialization will fail. This way we enforce all keys to be strings
- `ensure_ascii`: The RFC recommends `utf-8` for maximum interoperability. By setting `ensure_ascii` to `False` we allow unicode characters and python-rapidjson forces the encoding to `utf-8`.
- `sort_keys`: Sorted output by keys.

Every time we need to perform some operation on the data like calculating the hash or signing/verifying the transaction, we need to use the previous criteria to serialize the data and then use the `byte` representation of the serialized data (if we treat the data as bytes we eliminate possible encoding errors e.g. unicode characters). For example:
```python
# calculate the hash of a transaction
# the transaction is a dictionary
tx_serialized = bytes(serialize(tx))
tx_hash = hashlib.sha3_256(tx_serialized).hexdigest()

# signing a transaction
tx_serialized = bytes(serialize(tx))
signature = sk.sign(tx_serialized)

# verify signature
tx_serialized = bytes(serialize(tx))
pk.verify(signature, tx_serialized)
```
