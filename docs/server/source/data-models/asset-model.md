# The Digital Asset Model

To avoid redundant data in transactions, the digital asset model is different for `CREATE` and `TRANSFER` transactions.

A digital asset's properties are defined in a `CREATE` transaction with the following model:
```json
{
    "data": "<json document>"
}
```

For `TRANSFER` transactions we only keep the asset ID:
```json
{
    "id": "<asset's CREATE transaction ID (sha3-256 hash)>"
}
```


- `id`: The ID of the `CREATE` transaction that created the asset.
- `data`: A user supplied JSON document with custom information about the asset. Defaults to null.
