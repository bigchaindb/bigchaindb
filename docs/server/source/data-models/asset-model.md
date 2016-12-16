# The Digital Asset Model

To avoid redundant data in transactions, the digital asset model is different for `CREATE` and `TRANSFER` transactions.

A digital asset's properties are defined in a `CREATE` transaction with the following model:
```json
{
    "id": "<uuid>",
    "data": "<json document>"
}
```

For `TRANSFER` transactions we only keep the asset id.
```json
{
    "id": "<uuid>"
}
```


- `id`: UUID version 4 (random) converted to a string of hex digits in standard form. Added server side.
- `data`: A user supplied JSON document with custom information about the asset. Defaults to null.
