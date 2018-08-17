# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

from base58 import b58decode
import pytest


USER_PRIVATE_KEY = '8eJ8q9ZQpReWyQT5aFCiwtZ5wDZC4eDnCen88p3tQ6ie'
USER_PUBLIC_KEY = 'JEAkEJqLbbgDRAtMm8YAjGp759Aq2qTn9eaEHUj2XePE'

USER2_PRIVATE_KEY = 'F86PQPiqMTwM2Qi2Sda3U4Vdh3AgadMdX3KNVsu5wNJr'
USER2_PUBLIC_KEY = 'GDxwMFbwdATkQELZbMfW8bd9hbNYMZLyVXA3nur2aNbE'

USER3_PRIVATE_KEY = '4rNQFzWQbVwuTiDVxwuFMvLG5zd8AhrQKCtVovBvcYsB'
USER3_PUBLIC_KEY = 'Gbrg7JtxdjedQRmr81ZZbh1BozS7fBW88ZyxNDy7WLNC'

CC_FULFILLMENT_URI = (
    'pGSAINdamAGCsQq31Uv-08lkBzoO4XLz2qYjJa8CGmj3B1EagUDlVkMAw2CscpCG4syAboKKh'
    'Id_Hrjl2XTYc-BlIkkBVV-4ghWQozusxh45cBz5tGvSW_XwWVu-JGVRQUOOehAL'
)
CC_CONDITION_URI = ('ni:///sha-256;'
                    'eZI5q6j8T_fqv7xMROaei9_tmTMk4S7WR5Kr4onPHV8'
                    '?fpt=ed25519-sha-256&cost=131072')

ASSET_DEFINITION = {
    'data': {
        'definition': 'Asset definition'
    }
}

DATA = {
    'msg': 'Hello BigchainDB!'
}


@pytest.fixture
def user_priv():
    return USER_PRIVATE_KEY


@pytest.fixture
def user_pub():
    return USER_PUBLIC_KEY


@pytest.fixture
def user2_priv():
    return USER2_PRIVATE_KEY


@pytest.fixture
def user2_pub():
    return USER2_PUBLIC_KEY


@pytest.fixture
def user3_priv():
    return USER3_PRIVATE_KEY


@pytest.fixture
def user3_pub():
    return USER3_PUBLIC_KEY


@pytest.fixture
def ffill_uri():
    return CC_FULFILLMENT_URI


@pytest.fixture
def cond_uri():
    return CC_CONDITION_URI


@pytest.fixture
def user_Ed25519(user_pub):
    from cryptoconditions import Ed25519Sha256
    return Ed25519Sha256(public_key=b58decode(user_pub))


@pytest.fixture
def user_user2_threshold(user_pub, user2_pub):
    from cryptoconditions import ThresholdSha256, Ed25519Sha256
    user_pub_keys = [user_pub, user2_pub]
    threshold = ThresholdSha256(threshold=len(user_pub_keys))
    for user_pub in user_pub_keys:
        threshold.add_subfulfillment(
            Ed25519Sha256(public_key=b58decode(user_pub)))
    return threshold


@pytest.fixture
def user2_Ed25519(user2_pub):
    from cryptoconditions import Ed25519Sha256
    return Ed25519Sha256(public_key=b58decode(user2_pub))


@pytest.fixture
def user_input(user_Ed25519, user_pub):
    from bigchaindb.common.transaction import Input
    return Input(user_Ed25519, [user_pub])


@pytest.fixture
def user_user2_threshold_output(user_user2_threshold, user_pub, user2_pub):
    from bigchaindb.common.transaction import Output
    return Output(user_user2_threshold, [user_pub, user2_pub])


@pytest.fixture
def user_user2_threshold_input(user_user2_threshold, user_pub, user2_pub):
    from bigchaindb.common.transaction import Input
    return Input(user_user2_threshold, [user_pub, user2_pub])


@pytest.fixture
def user_output(user_Ed25519, user_pub):
    from bigchaindb.common.transaction import Output
    return Output(user_Ed25519, [user_pub])


@pytest.fixture
def user2_output(user2_Ed25519, user2_pub):
    from bigchaindb.common.transaction import Output
    return Output(user2_Ed25519, [user2_pub])


@pytest.fixture
def asset_definition():
    return ASSET_DEFINITION


@pytest.fixture
def data():
    return DATA


@pytest.fixture
def utx(user_input, user_output):
    from bigchaindb.common.transaction import Transaction
    return Transaction(Transaction.CREATE, {'data': None}, [user_input],
                       [user_output])


@pytest.fixture
def tx(utx, user_priv):
    return utx.sign([user_priv])


@pytest.fixture
def transfer_utx(user_output, user2_output, utx):
    from bigchaindb.common.transaction import (Input, TransactionLink,
                                               Transaction)
    user_output = user_output.to_dict()
    input = Input(utx.outputs[0].fulfillment,
                  user_output['public_keys'],
                  TransactionLink(utx.id, 0))
    return Transaction('TRANSFER', {'id': utx.id}, [input], [user2_output])


@pytest.fixture
def transfer_tx(transfer_utx, user_priv):
    return transfer_utx.sign([user_priv])


@pytest.fixture
def dummy_transaction():
    return {
        'asset': {'data': None},
        'id': 64 * 'a',
        'inputs': [{
            'fulfillment': 'dummy',
            'fulfills': None,
            'owners_before': [58 * 'a'],
        }],
        'metadata': None,
        'operation': 'CREATE',
        'outputs': [{
            'amount': '1',
            'condition': {
                'details': {
                    'public_key': 58 * 'b',
                    'type': 'ed25519-sha-256'
                },
                'uri': 'dummy',
            },
            'public_keys': [58 * 'b']
        }],
        'version': '2.0'
    }


@pytest.fixture
def unfulfilled_transaction():
    return {
        'asset': {
            'data': {
                'msg': 'Hello BigchainDB!',
            }
        },
        'id': None,
        'inputs': [{
            # XXX This could be None, see #1925
            # https://github.com/bigchaindb/bigchaindb/issues/1925
            'fulfillment': {
                'public_key': 'JEAkEJqLbbgDRAtMm8YAjGp759Aq2qTn9eaEHUj2XePE',
                'type': 'ed25519-sha-256'
            },
            'fulfills': None,
            'owners_before': ['JEAkEJqLbbgDRAtMm8YAjGp759Aq2qTn9eaEHUj2XePE']
        }],
        'metadata': None,
        'operation': 'CREATE',
        'outputs': [{
            'amount': '1',
            'condition': {
                'details': {
                    'public_key': 'JEAkEJqLbbgDRAtMm8YAjGp759Aq2qTn9eaEHUj2XePE',
                    'type': 'ed25519-sha-256'
                },
                'uri': 'ni:///sha-256;49C5UWNODwtcINxLgLc90bMCFqCymFYONGEmV4a0sG4?fpt=ed25519-sha-256&cost=131072'},
            'public_keys': ['JEAkEJqLbbgDRAtMm8YAjGp759Aq2qTn9eaEHUj2XePE']
        }],
        'version': '1.0'
    }


@pytest.fixture
def fulfilled_transaction():
    return {
        'asset': {
            'data': {
                'msg': 'Hello BigchainDB!',
            }
        },
        'id': None,
        'inputs': [{
            'fulfillment': ('pGSAIP_2P1Juh-94sD3uno1lxMPd9EkIalRo7QB014pT6dD9g'
                            'UANRNxasDy1Dfg9C2Fk4UgHdYFsJzItVYi5JJ_vWc6rKltn0k'
                            'jagynI0xfyR6X9NhzccTt5oiNH9mThEb4QmagN'),
            'fulfills': None,
            'owners_before': ['JEAkEJqLbbgDRAtMm8YAjGp759Aq2qTn9eaEHUj2XePE']
        }],
        'metadata': None,
        'operation': 'CREATE',
        'outputs': [{
            'amount': '1',
            'condition': {
                'details': {
                    'public_key': 'JEAkEJqLbbgDRAtMm8YAjGp759Aq2qTn9eaEHUj2XePE',
                    'type': 'ed25519-sha-256'
                },
                'uri': 'ni:///sha-256;49C5UWNODwtcINxLgLc90bMCFqCymFYONGEmV4a0sG4?fpt=ed25519-sha-256&cost=131072'},
            'public_keys': ['JEAkEJqLbbgDRAtMm8YAjGp759Aq2qTn9eaEHUj2XePE']
        }],
        'version': '1.0'
    }


# TODO For reviewers: Pick which approach you like best: parametrized or not?
@pytest.fixture(params=(
    {'id': None,
     'fulfillment': {
         'public_key': 'JEAkEJqLbbgDRAtMm8YAjGp759Aq2qTn9eaEHUj2XePE',
         'type': 'ed25519-sha-256'}},
    {'id': None,
     'fulfillment': ('pGSAIP_2P1Juh-94sD3uno1lxMPd9EkIalRo7QB014pT6dD9g'
                     'UANRNxasDy1Dfg9C2Fk4UgHdYFsJzItVYi5JJ_vWc6rKltn0k'
                     'jagynI0xfyR6X9NhzccTt5oiNH9mThEb4QmagN')},
    {'id': '7a7c827cf4ef7985f08f4e9d16f5ffc58ca4e82271921dfbed32e70cb462485f',
     'fulfillment': ('pGSAIP_2P1Juh-94sD3uno1lxMPd9EkIalRo7QB014pT6dD9g'
                     'UANRNxasDy1Dfg9C2Fk4UgHdYFsJzItVYi5JJ_vWc6rKltn0k'
                     'jagynI0xfyR6X9NhzccTt5oiNH9mThEb4QmagN')},
))
def tri_state_transaction(request):
    tx = {
        'asset': {
            'data': {
                'msg': 'Hello BigchainDB!',
            }
        },
        'id': None,
        'inputs': [{
            'fulfillment': None,
            'fulfills': None,
            'owners_before': ['JEAkEJqLbbgDRAtMm8YAjGp759Aq2qTn9eaEHUj2XePE']
        }],
        'metadata': None,
        'operation': 'CREATE',
        'outputs': [{
            'amount': '1',
            'condition': {
                'details': {
                    'public_key': 'JEAkEJqLbbgDRAtMm8YAjGp759Aq2qTn9eaEHUj2XePE',
                    'type': 'ed25519-sha-256'
                },
                'uri': 'ni:///sha-256;49C5UWNODwtcINxLgLc90bMCFqCymFYONGEmV4a0sG4?fpt=ed25519-sha-256&cost=131072'},
            'public_keys': ['JEAkEJqLbbgDRAtMm8YAjGp759Aq2qTn9eaEHUj2XePE']
        }],
        'version': '2.0'
    }
    tx['id'] = request.param['id']
    tx['inputs'][0]['fulfillment'] = request.param['fulfillment']
    return tx
