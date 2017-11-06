# The Asset Model

To avoid redundant data in transactions, the asset model is different for `CREATE` and `TRANSFER` transactions.

In a `CREATE` transaction, the `"asset"` must contain exactly one key-value pair. The key must be `"data"` and the value can be any valid JSON document, or `null`. For example:
```json
{
    "data": {
                "desc": "Gold-inlay bookmark owned by Xavier Bellomat Dickens III",
                "xbd_collection_id": 1857
            }
}
```

In a `TRANSFER` transaction, the `"asset"` must contain exactly one key-value pair. They key must be `"id"` and the value must contain a transaction ID (i.e. a SHA3-256 hash: the ID of the `CREATE` transaction which created the asset, which also serves as the asset ID). For example:
```json
{
    "id": "38100137cea87fb9bd751e2372abb2c73e7d5bcf39d940a5516a324d9c7fb88d"
}
```


.. note::

    When using MongoDB for storage certain restriction apply to all (including nested) keys of `"data"` JSON document i.e. valid keys should **not** begin with ``$`` character and cannot contain ``.`` or null character (Unicode code point 0000). Furthermore, the key `"language"` (at any level in the hierarchy) in `"data"` JSON document is a spcial key and used for specifying text search language. Its value must be one of the allowed values, see `Text search languages <https://docs.mongodb.com/manual/reference/text-search-languages/>`_ . It must be noted that only the languages supported by MongoDB community edition are allowed.



