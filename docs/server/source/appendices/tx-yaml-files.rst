The Transaction Schema Files
============================

BigchainDB checks all :ref:`transactions <The Transaction Model>`
(JSON documents) against a formal schema
defined in some JSON Schema files named
transaction.yaml,
transaction_create.yaml and
transaction_transfer.yaml.
The contents of those files are copied below.
To understand those contents
(i.e. JSON Schema), check out
`"Understanding JSON Schema"
<https://spacetelescope.github.io/understanding-json-schema/index.html>`_
by Michael Droettboom or
`json-schema.org <http://json-schema.org/>`_.


transaction.yaml
----------------

.. literalinclude:: ../../../../bigchaindb/common/schema/transaction.yaml
   :language: yaml


transaction_create.yaml
-----------------------

.. literalinclude:: ../../../../bigchaindb/common/schema/transaction_create.yaml
   :language: yaml


transaction_transfer.yaml
-------------------------

.. literalinclude:: ../../../../bigchaindb/common/schema/transaction_transfer.yaml
   :language: yaml
