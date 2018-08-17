<!---
Copyright BigchainDB GmbH and BigchainDB contributors
SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
Code is Apache-2.0 and docs are CC-BY-4.0
--->

# Generate a Key Pair for SSH

This page describes how to use `ssh-keygen`
to generate a public/private RSA key pair
that can be used with SSH.
(Note: `ssh-keygen` is found on most Linux and Unix-like
operating systems; if you're using Windows,
then you'll have to use another tool,
such as PuTTYgen.)

By convention, SSH key pairs get stored in the `~/.ssh/` directory.
Check what keys you already have there:
```text
ls -1 ~/.ssh/
```

Next, make up a new key pair name (called `<name>` below).
Here are some ideas:

* `aws-bdb-2`
* `tim-bdb-azure`
* `chris-bcdb-key`

Next, generate a public/private RSA key pair with that name:
```text
ssh-keygen -t rsa -C "<name>" -f ~/.ssh/<name>
```

It will ask you for a passphrase.
You can use whatever passphrase you like, but don't lose it.
Two keys (files) will be created in `~/.ssh/`:

1. `~/.ssh/<name>.pub` is the public key
2. `~/.ssh/<name>` is the private key
