<!---
Copyright BigchainDB GmbH and BigchainDB contributors
SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
Code is Apache-2.0 and docs are CC-BY-4.0
--->

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
are based on the [BigchainDB Transactions Specs](https://github.com/bigchaindb/BEPs/tree/master/tx-specs).
If you want to add a new transaction version,
you must write a spec for it first.
(You can't change the JSON Schema files for old versions.
Those were used to validate old transactions
and are needed to re-check those transactions.)

There used to be a file defining the JSON Schema for votes, named `vote.yaml`.
It was used by BigchainDB version 1.3.0 and earlier.
If you want a copy of the latest `vote.yaml` file,
then you can get it from the version 1.3.0 release on GitHub, at
[https://github.com/bigchaindb/bigchaindb/blob/v1.3.0/bigchaindb/common/schema/vote.yaml](https://github.com/bigchaindb/bigchaindb/blob/v1.3.0/bigchaindb/common/schema/vote.yaml).

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
