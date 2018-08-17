<!---
Copyright BigchainDB GmbH and BigchainDB contributors
SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
Code is Apache-2.0 and docs are CC-BY-4.0
--->

# Write Docs

If you're writing code, you should also update any related docs. However, you might want to write docs only, such as:

- General explainers
- Tutorials
- Courses
- Code explanations
- How BigchainDB relates to other blockchain things
- News from recent events

You can certainly do that!

- The docs for BigchainDB Server live under ``bigchaindb/docs/`` in the ``bigchaindb/bigchaindb`` repo.
- There are docs for the Python driver under ``bigchaindb-driver/docs/`` in the ``bigchaindb/bigchaindb-driver`` repo.
- There are docs for the JavaScript driver under ``bigchaindb/js-bigchaindb-driver`` in the ``bigchaindb/js-bigchaindb-driver`` repo.
- The source code for the BigchainDB website is in a private repo, but we can give you access if you ask.

The [BigchainDB Transactions Specs](https://github.com/bigchaindb/BEPs/tree/master/tx-specs/) (one for each spec version) are in the ``bigchaindb/BEPs`` repo.

You can write the docs using Markdown (MD) or RestructuredText (RST). Sphinx can understand both. RST is more powerful.

ReadTheDocs will automatically rebuild the docs whenever a commit happens on the ``master`` branch, or on one of the other branches that it is monitoring.
