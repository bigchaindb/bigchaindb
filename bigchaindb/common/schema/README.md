# Introduction

This directory contains the schemas for the different JSON documents BigchainDB uses.

The aim is to provide:
 - a strict definition/documentation of the data structures used in BigchainDB
 - a language independent tool to validate the structure of incoming/outcoming
   data (there are several ready to use
   [implementations](http://json-schema.org/implementations.html) written in
   different languages)

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
