# Introduction

This directory contains the schemas for the different JSON documents BigchainDB uses.

The aim is to provide:

- a strict definition of the data structures used in BigchainDB,
- a language-independent tool to validate the structure of incoming/outcoming
  data. (There are several ready to use
  [implementations](http://json-schema.org/implementations.html) written in
  different languages.)

## Sources

The files defining the JSON Schema for transactions (`transaction_*.yaml`)
are based on the [IPDB Transaction Spec](https://github.com/ipdb/ipdb-tx-spec).
If you want to add a new transaction version,
you must add it to the IPDB Transaction Spec first.
(You can't change the JSON Schema files for old versions.
Those were used to validate old transactions
and are needed to re-check those transactions.)

The file defining the JSON Schema for votes (`vote.yaml`) is BigchainDB-specific.

## Learn about JSON Schema

A good resource is [Understanding JSON Schema](http://spacetelescope.github.io/understanding-json-schema/index.html).
It provides a *more accessible documentation for JSON schema* than the [specs](http://json-schema.org/documentation.html).

## If it's supposed to be JSON, why's everything in YAML D:?

YAML is great for its conciseness and friendliness towards human-editing in comparision to JSON.

Although YAML is a superset of JSON, at the end of the day, JSON Schema processors, like
[json-schema](http://python-jsonschema.readthedocs.io/en/latest/), take in a native object (e.g.
Python dicts or JavaScript objects) as the schema used for validation. As long as we can serialize
the YAML into what the JSON Schema processor expects (almost always as simple as loading the YAML
like you would with a JSON file), it's the same as using JSON.

Specific advantages of using YAML:
 - Legibility, especially when nesting
 - Multi-line string literals, that make it easy to include descriptions that can be [auto-generated
   into Sphinx documentation](/docs/server/generate_schema_documentation.py)
