The vote.yaml File
==================

BigchainDB checks all :ref:`votes <The Vote Model>`
(JSON documents) against a formal schema
defined in a JSON Schema file named vote.yaml.
The contents of that file are copied below.
To understand those contents
(i.e. JSON Schema), check out
`"Understanding JSON Schema"
<https://spacetelescope.github.io/understanding-json-schema/index.html>`_
by Michael Droettboom or
`json-schema.org <http://json-schema.org/>`_.

.. literalinclude:: ../../../../bigchaindb/common/schema/vote.yaml
   :language: yaml
