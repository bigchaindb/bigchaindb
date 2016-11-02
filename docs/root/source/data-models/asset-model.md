# The Digital Asset Model

To avoid redundant data in transactions, the digital asset model is different for `CREATE` and `TRANSFER` transactions.

A digital asset's properties are defined in a `CREATE` transaction with the following model:
```json
{
    "id": "<uuid>",
    "divisible": "<true | false>",
    "updatable": "<true | false>",
    "refillable": "<true | false>",
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
- `divisible`: Whether the asset is divisible or not. Defaults to false.
- `updatable`: Whether the data in the asset can be updated in the future or not. Defaults to false.
- `refillable`: Whether the amount of the asset can change after its creation. Defaults to false.
- `data`: A user supplied JSON document with custom information about the asset. Defaults to null.
- _amount_: The amount of "shares". Only relevant if the asset is marked as divisible. Defaults to 1. The amount is not specified in the asset, but in the conditions (see next section).

At the time of this writing divisible, updatable, and refillable assets are not yet implemented.
See [Issue #487 on Github](https://github.com/bigchaindb/bigchaindb/issues/487)