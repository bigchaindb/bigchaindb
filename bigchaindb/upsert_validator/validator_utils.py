import codecs

from abci.types_pb2 import (Validator,
                            PubKey)
from bigchaindb.tendermint_utils import public_key_to_base64


def encode_validator(v):
    ed25519_public_key = v['public_key']
    # NOTE: tendermint expects public to be encoded in go-amino format
    pub_key = PubKey(type='ed25519',
                     data=bytes.fromhex(ed25519_public_key))
    return Validator(pub_key=pub_key,
                     address=b'',
                     power=v['power'])


def decode_validator(v):
    return {'pub_key': {'type': v.pub_key.type,
                        'data': codecs.encode(v.pub_key.data, 'base64').decode().rstrip('\n')},
            'voting_power': v.power}


def new_validator_set(validators, height, updates):
    validators_dict = {}
    for v in validators:
        validators_dict[v['pub_key']['data']] = v

    updates_dict = {}
    for u in updates:
        public_key64 = public_key_to_base64(u['public_key'])
        updates_dict[public_key64] = {'pub_key': {'type': 'ed25519',
                                                  'data': public_key64},
                                      'voting_power': u['power']}

    new_validators_dict = {**validators_dict, **updates_dict}
    return list(new_validators_dict.values())
