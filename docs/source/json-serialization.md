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

After looking at this further, we decided that the python json module is still the best bet because it complies with the RFC. We can specify the encoding, separators used and enforce it to order by the keys to make sure that we obtain maximum interoperability.

```python
import json

json.dumps(data, skipkeys=False, ensure_ascii=False,
           encoding="utf-8", separators=(',', ':'),
           sort_keys=True)
```

- `skipkeys`: With skipkeys `False` if the provided keys are not a string the serialization will fail. This way we enforce all keys to be strings
- `ensure_ascii`: The RFC recommends `utf-8` for maximum interoperability. By setting `ensure_ascii` to `False` we allow unicode characters and force the encoding to `utf-8`.
- `separators`: We need to define a standard separator to use in the serialization. We did not do this different implementations could use different separators for serialization resulting in a still valid transaction but with a different hash e.g. an extra whitespace introduced in the serialization would not still create a valid JSON object but the hash would be different.

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
vk.verify(signature, tx_serialized)
```
