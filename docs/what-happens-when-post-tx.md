# What happens when I post a transaction to BigchainDB test network!

Imagine I have a bigchaindb test network deployed at https://test.bigchaindb.com and I wish to post a transaction to this network.
I'd probably type something like this in my terminal:

```bash
curl -XPOST https://test.bigchaindb.com -d @tx_data.json
```

and hit enter. After a few seconds, I should see the confirmation of my transaction being successful or bein rejected. It works and that's great! But what's really going on under the hood?

This is a living document. If you spot areas that can be improved or rewritten, contributions are welcome!
