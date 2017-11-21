The Transaction Schema Files
============================

BigchainDB checks all :ref:`transactions <The Transaction Model>`
against a formal schema
defined in some JSON Schema files.
The contents of those files are copied below.
To understand those contents
(i.e. JSON Schema), check out
`"Understanding JSON Schema"
<https://spacetelescope.github.io/understanding-json-schema/index.html>`_
by Michael Droettboom or
`json-schema.org <http://json-schema.org/>`_.


transaction_v1.0.yaml
---------------------

.. literalinclude:: ../../../../bigchaindb/common/schema/transaction_v1.0.yaml
   :language: yaml


transaction_create_v1.0.yaml
----------------------------

.. literalinclude:: ../../../../bigchaindb/common/schema/transaction_create_v1.0.yaml
   :language: yaml


transaction_transfer_v1.0.yaml
------------------------------

.. literalinclude:: ../../../../bigchaindb/common/schema/transaction_transfer_v1.0.yaml
   :language: yaml
