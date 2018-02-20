# What happens when I post a transaction to bigchaindb network!

Imagine I have BigchainDB test network deployed and I want to POST a transaction to this network.
I'd probably type something like this in my terminal:

```bash
curl -XPOST http://test.bigchaindb.com/transactions -d @transaction_data.json
```

and hit enter. After a few seconds, I should see the confirmation of transaction being successful or transaction being rejected and that's great! But what's really going on under the hood?

This is a living document. If you spot areas that can be improved or rewritten, contributions are welcome
