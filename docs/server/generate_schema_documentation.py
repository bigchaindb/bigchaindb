""" Script to render transaction schema into .rst document """

import os.path

from bigchaindb.common.schema import TX_SCHEMA_ORDERED as TX


TPL_PROP = """\
%(title)s
%(underline)s

**type:** %(type)s

%(description)s
"""


TPL_DOC = """\
==================
Transaction Schema
==================

* `Transaction`_

* `Transaction Body`_

* Condition_

* Fulfillment_

* Asset_

* Metadata_

* Timestamp_

.. raw:: html

    <style>
    #transaction-schema h2 {
         border-top: solid 3px #6ab0de;
         background-color: #e7f2fa;
         padding: 5px;
    }
    #transaction-schema h3 {
         background: #f0f0f0;
         border-left: solid 3px #ccc;
         font-weight: bold;
         padding: 6px;
         font-size: 100%%;
         font-family: monospace;
    }
    </style>

Transaction
-----------

%(wrapper)s

Transaction Body
----------------

%(transaction)s

Condition
----------

%(condition)s

Fulfillment
-----------

%(fulfillment)s

Asset
-----

%(asset)s

Metadata
--------

%(metadata)s
"""


def render_section(section_name, obj):
    """ Render a domain object and it's properties """
    out = [obj['description']]
    for name, prop in obj.get('properties', {}).items():
        try:
            title = '%s.%s' % (section_name, name)
            out += [TPL_PROP % {
                'title': title,
                'underline': '^' * len(title),
                'description': property_description(prop),
                'type': property_type(prop),
            }]
        except Exception as exc:
            raise ValueError("Error rendering property: %s" % name, exc)
    return '\n\n'.join(out + [''])


def property_description(prop):
    """ Get description of property """
    if 'description' in prop:
        return prop['description']
    if '$ref' in prop:
        return property_description(resolve_ref(prop['$ref']))
    if 'anyOf' in prop:
        return property_description(prop['anyOf'][0])
    raise KeyError("description")


def property_type(prop):
    """ Resolve a string representing the type of a property """
    if 'type' in prop:
        if prop['type'] == 'array':
            return 'array (%s)' % property_type(prop['items'])
        return prop['type']
    if 'anyOf' in prop:
        return ' or '.join(property_type(p) for p in prop['anyOf'])
    if '$ref' in prop:
        return property_type(resolve_ref(prop['$ref']))
    raise ValueError("Could not resolve property type")


def resolve_ref(ref):
    """ Resolve reference """
    assert ref.startswith('#/definitions/')
    return TX['definitions'][ref[14:]]


def main():
    """ Main function """
    doc = TPL_DOC % {
        'wrapper': render_section('transaction', TX),
        'transaction': render_section('transaction',
                                      TX['properties']['transaction']),
        'condition': render_section('conditions',
                                    TX['definitions']['condition']),
        'fulfillment': render_section('fulfillment',
                                      TX['definitions']['fulfillment']),
        'asset': render_section('asset',
                                TX['definitions']['asset']),
        'metadata': render_section('metadata',
                                   TX['definitions']['metadata']['anyOf'][0]),
    }

    path = os.path.join(os.path.dirname(__file__), 'source/schema.rst')

    open(path, 'w').write(doc)


if __name__ == '__main__':
    main()
