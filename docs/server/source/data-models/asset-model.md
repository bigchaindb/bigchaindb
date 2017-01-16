# The Digital Asset Model

The asset ID is the same as the ID of the CREATE transaction that defined the asset.

In the case of a CREATE transaction, the transaction ID is duplicated into the asset object for clarity and consistency in the database. The CREATE transaction also contains a user definable payload to describe the asset:
```json
{
    "id": "<same as transaction ID (sha3-256 hash)>",
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
