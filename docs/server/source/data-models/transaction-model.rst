The Transaction Model
=====================

See the `IPDB Transaction Spec <https://github.com/ipdb/ipdb-tx-spec>`_.


The Transaction Schema
----------------------

BigchainDB checks all transactions (JSON documents)
against a formal schema defined
in some `JSON Schema <http://json-schema.org/>`_ files.
Those files are part of the 
`IPDB Transaction Spec <https://github.com/ipdb/ipdb-tx-spec>`_.
Their official source is the ``tx_schema/`` directory
in the `ipdb/ipdb-tx-spec repository on GitHub
<https://github.com/ipdb/ipdb-tx-spec>`_,
but BigchainDB Server uses copies of those files;
those copies can be found
in the ``bigchaindb/common/schema/`` directory
in the `bigchaindb/bigchaindb repository on GitHub
<https://github.com/bigchaindb/bigchaindb>`_.
