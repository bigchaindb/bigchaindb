# Crypto Conditions

This spec is from the [**Interledger Protocol (ILP)**]
(https://interledger.org/five-bells-condition/spec.html)

## Motivation

We would like a way to describe a signed message such that multiple actors in a distributed system can all verify the same signed message and agree on whether it matches the description.

This provides a useful primitive for distributed, event-based systems since we can describe events (represented by signed messages) and therefore define generic authenticated event handlers.

## Terminology

* ##### Condition
  A condition is the hash of a description of a signed message.

* ##### Fulfillment
  A fulfillment consists of a description of a signed message and a signed message that matches the description.

  The description can be hashed and compared to a condition. If the message matches the description and the hash of the description matches the condition, we say that the fulfillment **fulfills** the condition.

* ##### Hashlock
  A tuple consisting of a bytestring and its hash where the hash is published first and the publication of the corresponding bytestring acts as a one-bit, one-time signature.

# Basic Format

## Bitmask

Any system accepting crypto-conditions must be able to state its supported
algorithms. It must be possible to verify that all algorithms used in a certain
condition are indeed supported even if the fulfillment is not available yet.

In order to meet these design goals, we define a bitmask to express the supported primitives.

The following bits are assigned:

|Type Bit |Exp.         |Int.|Condition Type   |
|--------:|------------:|---:|-----------------|
|        1|2<sup>0</sup>|   1|SHA-256          |
|       10|2<sup>1</sup>|   2|RSA-SHA-256      |
|      100|2<sup>2</sup>|   4|THRESHOLD-SHA-256|
|     1000|2<sup>3</sup>|   8|ED25519-SHA-256  |

Conditions contain a bitmask of types they require the implementation to support. Implementations provide a bitmask of types they support.

### ILP Features

Crypto-conditions are a simple multi-algorithm, multi-message, multi-level, multi-signature standard.

* **Multi-algorithm**

  Crypto-conditions can support several different signature and hash algorithms and support for new ones can be added in the future.

  Implementations can state their supported algorithms simply by providing a bitmask. It is easy to verify that a given implementation will be able to verify the fulfillment to a given condition, by verifying that the condition's bitmask `condition` and its own bitmask of supported algorithms `supported` satisfies `condition & ~supported == 0` where `&` is the bitwise AND operator and `~` is the bitwise NOT operator.

  Any new high bit can redefine the meaning of any existing lower bits as long as it is set. This can be used to remove obsolete algorithms.

  The bitmask is encoded as a varint to minimize space usage.

* **Multi-signature**

  Crypto-conditions can abstract away many of the details of multi-sign. When a party provides a condition, other parties can treat it opaquely and do not need to know about its internal structure. That allows parties to define arbitrary multi-signature setups without breaking compatibility.

  Protocol designers can use crypto-conditions as a drop-in replacement for public key signature algorithms and add multi-signature support to their protocols without adding any additional complexity.

* **Multi-level**

  Basic multi-sign is single-level and does not support more complex trust relationships such as "I trust Alice and Bob, but only when Candice also agrees". In single level 2-of-3 Alice and Bob could sign on their own, without Candice's approval.

  Crypto-conditions add that flexibility elegantly, by applying thresholds not just to signatures, but to conditions which can be signatures or further conditions. That allows the creation of an arbitrary threshold boolean circuit of signatures.

* **Multi-message**

  Crypto-conditions can sign not just one, but multiple messages at the same time and by different people. These messages can then be used as inputs for other algorithms.

  This allows resource-controlling systems to perform their functions without knowing the details of the higher-level protocols that these functions are a part of.

## Usage

```python
import binascii
from bigchaindb.crypto.condition import Condition
from bigchaindb.crypto.fulfillment import Fulfillment
from bigchaindb.crypto.fulfillments.sha256 import Sha256Fulfillment

# Parse a condition from a URI
example_condition_uri = 'cc:1:1:47DEQpj8HBSa-_TImW-5JCeuQeRkm5NMpJWZG3hSuFU:1'
parsed_condition = Condition.from_uri(example_condition_uri)
print(isinstance(parsed_condition, Condition))
# prints True

print(binascii.hexlify(parsed_condition.hash))
# prints b'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'

# Compile a condition
parsed_condition_uri = parsed_condition.serialize_uri()
print(parsed_condition_uri)
# prints 'cc:1:1:47DEQpj8HBSa-_TImW-5JCeuQeRkm5NMpJWZG3hSuFU:1'
print(parsed_condition_uri == example_condition_uri)
# prints True

# Parse a fulfillment
example_fulfillment_uri = 'cf:1:1:AA'
parsed_fulfillment = Fulfillment.from_uri(example_fulfillment_uri)
print(isinstance(parsed_fulfillment, Sha256Fulfillment))
# prints True
# Note: Merely parsing a fulfillment DOES NOT validate it.

# Validate a fulfillment
parsed_fulfillment.validate()
# prints True
```

## ILP Encoding

### Binary types

* **VARUINT**

  Unsigned variable-length integer. Implementation matches [Base128 Varints](https://developers.google.com/protocol-buffers/docs/encoding#varints) in Protocol Buffers. Implementations MAY define different maximum lengths for their varints, as long as that length is long enough to cover their bitmask and their maximum supported fulfillment length. (This is safe, because no larger varuint can appear in a valid crypto-condition.)

* **VARBYTES**

  Consists of a `VARUINT` length field followed by that many bytes.

* **VARARRAY**

  Consists of a `VARUINT` length fields followed by that many bytes filled with elements of the array.

### String types

* **BASE10**

  Variable-length integer encoded as a base-10 (decimal) number. Implementations MUST reject encodings that are too large for them to parse. Implementations MUST be tested for overflows.

* **BASE16**

  Variable-length integer encoded as a base-16 (hexadecimal) number. Implementations MUST reject encodings that are too large for them to parse. Implementations MUST be tested for overflows. No leading zeros.

* **BASE64URL**

  Base64-URL encoding. See [RFC4648 Section 5](https://tools.ietf.org/html/rfc4648#section-5).

### Condition

Conditions are ASCII encoded as:

```
"cc:" BASE10(VERSION) ":" BASE16(TYPE_BITMASK) ":" BASE64URL(HASH) ":" BASE10(MAX_FULFILLMENT_LENGTH)
```

Conditions are binary encoded as:

```
CONDITION =
  VARUINT TYPE_BITMASK
  VARBYTES HASH
  VARUINT MAX_FULFILLMENT_LENGTH
```

The `TYPE_BITMASK` is the boolean OR of the `TYPE_BIT`s of the condition type and all subcondition types, recursively.

### Fulfillment

Fulfillments are ASCII encoded as:

```
"cf:" BASE10(VERSION) ":" BASE16(TYPE_BIT) ":" BASE64URL(FULFILLMENT_PAYLOAD)
```

Fulfillments are binary encoded as:

```
FULFILLMENT =
  VARUINT TYPE_BIT
  FULFILLMENT_PAYLOAD
```

The `TYPE_BIT` is the single bit representing the top level condition type.

# Condition Types

## SHA-256

SHA-256 is assigned the type bit 2<sup>0</sup> = 0x01.

### Notes

This type of condition is also called a hashlock. We can use revealing the preimage as a type of one bit signature.

Bitcoin supports this type of condition via the `OP_HASH256` operator

### Condition

```
HASH = SHA256(PREIMAGE)
```

### Fulfillment

```
FULFILLMENT_PAYLOAD =
  VARBYTES PREIMAGE
```

### Usage

```python
import binascii, hashlib
from bigchaindb.crypto.condition import Condition
from bigchaindb.crypto.fulfillments.sha256 import Sha256Fulfillment

secret = ''
puzzle = binascii.hexlify(hashlib.sha256(secret.encode()).digest())
print(puzzle)
# prints b'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'

# Create a SHA256 condition
sha256condition = Condition()
sha256condition.bitmask = 0x01
sha256condition.hash = binascii.unhexlify(puzzle)
sha256condition.max_fulfillment_length = 1
sha256condition_uri = sha256condition.serialize_uri()
print(sha256condition_uri)
# prints 'cc:1:1:47DEQpj8HBSa-_TImW-5JCeuQeRkm5NMpJWZG3hSuFU:1'

# Create a fulfillment
sha256fulfillment = Sha256Fulfillment()

# Create a condition from fulfillment
sha256fulfillment.condition
# raises ValueError: Could not calculate hash, no preimage provided
sha256fulfillment.preimage = secret
print(sha256fulfillment.condition.serialize_uri() == sha256condition_uri)
# prints True

# Compile a fulfillment
print(sha256fulfillment.serialize_uri())
# prints 'cf:1:1:AA'

# Even better: verify that the fulfillment matches the condition
print(sha256fulfillment.validate() and \
    sha256fulfillment.condition.serialize_uri() == sha256condition.serialize_uri())
# prints True
```

## RSA-SHA-256

RSA-SHA-256 is assigned the type bit 2<sup>1</sup> = 0x02.

**Warning:** not (yet) implemented in BigchainDB, for info see the [**ILP specification**](https://interledger.org/five-bells-condition/spec.html)


## ED25519-SHA-256

ED25519-SHA-256 is assigned the type bit 2<sup>3</sup> = 0x08.

### Condition

```
HASH = SHA256(
  VARBYTES PUBLIC_KEY
  VARBYTES MESSAGE_ID
  VARBYTES FIXED_PREFIX
  VARUINT DYNAMIC_MESSAGE_LENGTH
)
```

### Fulfillment

```
FULFILLMENT_PAYLOAD =
  VARBYTES PUBLIC_KEY
  VARBYTES MESSAGE_ID
  VARBYTES FIXED_PREFIX
  VARUINT DYNAMIC_MESSAGE_LENGTH
  VARBYTES DYNAMIC_MESSAGE
  VARBYTES SIGNATURE
```

The `DYNAMIC_MESSAGE_LENGTH` is included to provide a maximum length for `DYNAMIC_MESSAGE` even if the actual message suffix length is different. This value is used to calculate the `MAX_FULFILLMENT_LENGTH` in the condition.

The `MESSAGE_ID` represents an identifier for the message. All messages in a cryptocondition that have a common identifier must match, otherwise the condition is invalid. Implementations may return messages as a map of `MESSAGE_ID` => `MESSAGE` pairs.

The message to be signed is the concatenation of the `FIXED_PREFIX` and `DYNAMIC_MESSAGE`.

The `MESSAGE_ID`, `FIXED_PREFIX`, `DYNAMIC_MESSAGE_LENGTH` and `DYNAMIC_MESSAGE` fields have the same meaning as in the [**RSA-SHA-256 condition type**](https://interledger.org/five-bells-condition/spec.html).

### Usage

```python
from bigchaindb.crypto.ed25519 import Ed25519SigningKey, Ed25519VerifyingKey
from bigchaindb.crypto.fulfillments.ed25519_sha256 import Ed25519Sha256Fulfillment

# We use base58 key encoding
sk = Ed25519SigningKey(b'9qLvREC54mhKYivr88VpckyVWdAFmifJpGjbvV5AiTRs')
vk = sk.get_verifying_key()

# Create an ED25519-SHA256 condition
ed25519_fulfill`nt = Ed25519Sha256Fulfillment()
ed25519_fulfillment.public_key = vk
ed25519_fulfillment.message_prefix = 'Hello world!'
ed25519_fulfillment.max_dynamic_message_length = 32  # defaults to 0
ed25519_condition_uri = ed25519_fulfillment.condition.serialize_uri()
print (ed25519_condition_uri)
# prints 'cc:1:8:qQINW2um59C4DB9JSVXH1igqAmaYGGqryllHUgCpfPU:113'

# ED25519-SHA256 condition not fulfilled
print(ed25519_fulfillment.validate())
# prints False

# Fulfill an ED25519-SHA256 condition
ed25519_fulfillment.message = ' Conditions are here!'
ed25519_fulfillment.sign(sk)
print(ed25519_fulfillment.validate())
# prints True

print(ed25519_fulfillment.serialize_uri())
# prints 'cf:1:8:IOwXK5OtXlY79JMscOEkUDTDVGfvLv1NZOv4GWg0Z-K_DEhlbGxvIHdvcmxkISAVIENvbmRpdGlvbnMgYXJlIGhlcmUhQENbql531PbCJlRUvKjP56k0XKJMOrIGo2F66ueuTtRnYrJB2t2ZttdfXM4gzD_87eH1nZTpu4rTkAx81hSdpwI'
print (ed25519_fulfillment.condition.serialize_uri())

# Parse a fulfillment URI
parsed_ed25519_fulfillment = Ed25519Sha256Fulfillment.from_uri('cf:1:8:IOwXK5OtXlY79JMscOEkUDTDVGfvLv1NZOv4GWg0Z-K_DEhlbGxvIHdvcmxkISAVIENvbmRpdGlvbnMgYXJlIGhlcmUhQENbql531PbCJlRUvKjP56k0XKJMOrIGo2F66ueuTtRnYrJB2t2ZttdfXM4gzD_87eH1nZTpu4rTkAx81hSdpwI')
        
print(parsed_ed25519_fulfillment.validate())
# prints True
print(parsed_ed25519_fulfillment.condition.serialize_uri())
# prints 'cc:1:8:qQINW2um59C4DB9JSVXH1igqAmaYGGqryllHUgCpfPU:113'
```

### Implementation

The exact algorithm and encodings used for `PUBLIC_KEY` and `SIGNATURE` are Ed25519 as defined in [draft-irtf-cfrg-eddsa-04](https://datatracker.ietf.org/doc/draft-irtf-cfrg-eddsa/).

## THRESHOLD-SHA-256

THRESHOLD-SHA-256 is assigned the type bit 2<sup>2</sup> = 0x04.

### Condition

```
HASH = SHA256(
  VARUINT TYPE_BIT
  VARUINT THRESHOLD
  VARARRAY
    VARUINT WEIGHT
    CONDITION
)
```

The `TYPE_BIT` is `0x04`. The reason we need this is because threshold conditions are a structural condition. Structural conditions can have subconditions, meaning their TYPE_BITMASK can have multiple bits set, including other structural conditions. This `TYPE_BIT` prevents the possibility that two different structural fulfillments could ever generate the exact same condition.

The `VARARRAY` of conditions is sorted first based on length, shortest first. Elements of the same length are sorted in lexicographic (big-endian) order, smallest first.

### Fulfillment

```
FULFILLMENT_PAYLOAD =
  VARUINT THRESHOLD
  VARARRAY
    VARUINT WEIGHT
    FULFILLMENT
  VARARRAY
    VARUINT WEIGHT
    CONDITION
```

### Usage

```python
from bigchaindb.crypto.fulfillments.sha256 import Sha256Fulfillment
from bigchaindb.crypto.fulfillments.ed25519_sha256 import Ed25519Sha256Fulfillment
from bigchaindb.crypto.fulfillments.threshold_sha256 import ThresholdSha256Fulfillment

# Parse some fulfillments
sha256_fulfillment = Sha256Fulfillment.from_uri('cf:1:1:AA')
ed25519_fulfillment = Ed25519Sha256Fulfillment.from_uri('cf:1:8:IOwXK5OtXlY79JMscOEkUDTDVGfvLv1NZOv4GWg0Z-K_DEhlbGxvIHdvcmxkISAVIENvbmRpdGlvbnMgYXJlIGhlcmUhQENbql531PbCJlRUvKjP56k0XKJMOrIGo2F66ueuTtRnYrJB2t2ZttdfXM4gzD_87eH1nZTpu4rTkAx81hSdpwI')

# Create a threshold condition
theshold_fulfillment = ThresholdSha256Fulfillment()
theshold_fulfillment.add_subfulfillment(sha256_fulfillment)
theshold_fulfillment.add_subfulfillment(ed25519_fulfillment)
theshold_fulfillment.threshold = 1
print(theshold_fulfillment.condition.serialize_uri())
# prints 'cc:1:d:9DdkQtOl2m9yjqZzCg6ck5b2zM3tAPLlJMaHsKkszIA:114'

# Compile a threshold fulfillment
theshold_fulfillment_uri = theshold_fulfillment.serialize_uri()
# Note: If there are more than enough fulfilled subconditions, shorter
# fulfillments will be chosen over longer ones.
print(theshold_fulfillment_uri)
# prints 'cf:1:4:AQEBAQABAQggqQINW2um59C4DB9JSVXH1igqAmaYGGqryllHUgCpfPVx'

# Validate fulfillment
print(theshold_fulfillment.validate())
# prints True

# Parse the fulfillment
reparsed_fulfillment = ThresholdSha256Fulfillment.from_uri(theshold_fulfillment_uri)
print(reparsed_fulfillment.validate())
# prints True

# Increase threshold
theshold_fulfillment.threshold = 3
print(theshold_fulfillment.validate())
# prints False

```