# Notes on Our Release Process

"Our Release Process" is our release process for BigchainDB Server, not something else.

It hasn't been revised for [C4](https://github.com/bigchaindb/BEPs/tree/master/1) yet. It should be. That will simplify it a lot. Releases are just tags on the ``master`` branch. There are no topic branches!

Minor releases (X.Y.Z) and major releases (X.Y) are all just Git tags (named commits). There are no branches.

What if 2.4 is out but now you want to release an update to 2.3.1 named 2.3.2? Easy, create a whole new repository and let the `master` branch over in that repository represent the 2.3.x history.
